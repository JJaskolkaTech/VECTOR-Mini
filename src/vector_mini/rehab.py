"""Synthetic sEMG-to-assistance rehabilitation research simulation.

This module models a software-in-the-loop signal path.  It does not produce
stimulation parameters and must not be connected to a person or stimulator.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _smoothstep(value: float) -> float:
    value = _clamp(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


class AssistState(str, Enum):
    READY = "READY"
    ASSISTING = "ASSISTING"
    E_STOP = "E_STOP"


class AssistFault(str, Enum):
    NONE = "NONE"
    SIGNAL_INVALID = "SIGNAL_INVALID"
    ELECTRODE_CONTACT = "ELECTRODE_CONTACT"
    PLACEMENT_INVALID = "PLACEMENT_INVALID"
    ASSIST_TIMEOUT = "ASSIST_TIMEOUT"
    EXTERNAL_E_STOP = "EXTERNAL_E_STOP"


@dataclass(frozen=True)
class RehabConfig:
    """Configuration for the deterministic research simulation.

    Values associated with the assistance channel are normalized software
    quantities, not electrical current, pulse width, or frequency.
    """

    sample_rate_hz: int = 250
    duration_s: float = 5.0
    intent_onset_s: float = 0.85
    intent_release_s: float = 3.55
    baseline_end_s: float = 0.65
    rms_window_s: float = 0.060
    calibrated_activation_rms: float = 0.115
    confidence_on: float = 0.58
    confidence_off: float = 0.34
    confidence_dwell_s: float = 0.080
    max_assist_duration_s: float = 3.20
    max_assist_command: float = 0.85
    max_stimulation_command: float = 0.70
    max_stimulation_ramp_per_s: float = 0.90
    max_kinetic_command: float = 0.55
    min_electrode_contact_quality: float = 0.75
    min_placement_alignment: float = 0.80
    target_extension_deg: float = 55.0

    @property
    def dt_s(self) -> float:
        return 1.0 / self.sample_rate_hz


@dataclass(frozen=True)
class RehabSample:
    timestamp_s: float
    reference_emg_norm: float
    impaired_emg_norm: float
    reference_envelope: float
    impaired_envelope: float
    intent_confidence: float
    intent_detected: bool
    electrode_contact_quality: float
    placement_alignment: float
    dose_request_norm: float
    stimulation_command_norm: float
    kinetic_command_norm: float
    target_angle_deg: float
    unassisted_angle_deg: float
    assisted_angle_deg: float
    safety_state: AssistState
    fault: AssistFault


@dataclass(frozen=True)
class RehabSummary:
    intent_detected_at_s: float | None
    peak_confidence: float
    reference_peak_envelope: float
    impaired_peak_envelope: float
    unassisted_peak_deg: float
    assisted_peak_deg: float
    unassisted_rmse_deg: float
    assisted_rmse_deg: float
    tracking_error_reduction_pct: float
    final_state: AssistState
    final_fault: AssistFault


@dataclass(frozen=True)
class VirtualElectrodeSetup:
    """Abstract electrode checks for the virtual subject.

    Channel names identify functions, not anatomical placement instructions.
    Quality and alignment are unitless simulation values in the range 0..1.
    """

    sensing_channel: str = "SENSE-A · target-muscle sEMG"
    stimulation_channel: str = "STIM-A/B · virtual target-muscle pair"
    sensing_contact_quality: float = 0.96
    stimulation_contact_quality: float = 0.93
    placement_alignment: float = 0.92

    @property
    def minimum_contact_quality(self) -> float:
        return min(self.sensing_contact_quality, self.stimulation_contact_quality)


class NormalizedDoseController:
    """Slew-limit a virtual stimulation command; contains no clinical dose."""

    def __init__(self, config: RehabConfig) -> None:
        self.config = config
        self.output = 0.0

    def update(self, requested: float, authorized: bool) -> float:
        if not authorized:
            self.output = 0.0
            return self.output
        target = _clamp(requested, 0.0, self.config.max_stimulation_command)
        max_step = self.config.max_stimulation_ramp_per_s * self.config.dt_s
        delta = _clamp(target - self.output, -max_step, max_step)
        self.output = _clamp(
            self.output + delta,
            0.0,
            self.config.max_stimulation_command,
        )
        return self.output


class IntentEstimator:
    """Streaming, personalized envelope-and-trend intent estimator."""

    def __init__(self, config: RehabConfig, baseline_rms: float) -> None:
        self.config = config
        self.baseline_rms = baseline_rms
        self.confidence = 0.0
        self.previous_envelope = baseline_rms
        self.above_threshold_s = 0.0
        self.detected = False

    def update(self, envelope: float, valid: bool = True) -> tuple[float, bool]:
        if not valid or not math.isfinite(envelope):
            self.confidence = 0.0
            self.detected = False
            self.above_threshold_s = 0.0
            return self.confidence, self.detected

        activation_span = max(
            self.config.calibrated_activation_rms - self.baseline_rms,
            1e-6,
        )
        normalized = _clamp(
            (envelope - self.baseline_rms) / activation_span,
            0.0,
            1.0,
        )
        positive_trend = _clamp(
            (envelope - self.previous_envelope) / (activation_span * 0.12),
            0.0,
            1.0,
        )
        evidence = 0.84 * normalized + 0.16 * positive_trend
        alpha = 1.0 - math.exp(-self.config.dt_s / 0.055)
        self.confidence += alpha * (evidence - self.confidence)
        self.previous_envelope = envelope

        if not self.detected:
            if self.confidence >= self.config.confidence_on:
                self.above_threshold_s += self.config.dt_s
                if self.above_threshold_s + 1e-12 >= self.config.confidence_dwell_s:
                    self.detected = True
            else:
                self.above_threshold_s = 0.0
        elif self.confidence < self.config.confidence_off:
            self.detected = False
            self.above_threshold_s = 0.0
        return self.confidence, self.detected


class AssistSafetyGate:
    """Fail-closed authorization for a normalized assistance request."""

    def __init__(self, config: RehabConfig) -> None:
        self.config = config
        self.state = AssistState.READY
        self.latched_fault = AssistFault.NONE
        self.assist_started_at_s: float | None = None

    @property
    def locked(self) -> bool:
        return self.latched_fault is not AssistFault.NONE

    def trip(self, fault: AssistFault) -> None:
        if fault is AssistFault.NONE:
            raise ValueError("cannot latch AssistFault.NONE")
        if not self.locked:
            self.latched_fault = fault
        self.state = AssistState.E_STOP

    def authorize(
        self,
        requested: float,
        now_s: float,
        confidence: float,
        intent_detected: bool,
        electrode_contact_quality: float,
        placement_alignment: float,
        signal_valid: bool = True,
        external_estop: bool = False,
    ) -> float:
        values_valid = all(
            math.isfinite(value)
            for value in (
                requested,
                confidence,
                electrode_contact_quality,
                placement_alignment,
            )
        )
        if external_estop:
            self.trip(AssistFault.EXTERNAL_E_STOP)
        elif not signal_valid or not values_valid:
            self.trip(AssistFault.SIGNAL_INVALID)
        elif electrode_contact_quality < self.config.min_electrode_contact_quality:
            self.trip(AssistFault.ELECTRODE_CONTACT)
        elif placement_alignment < self.config.min_placement_alignment:
            self.trip(AssistFault.PLACEMENT_INVALID)

        if self.locked:
            return 0.0

        if not intent_detected or confidence < self.config.confidence_off:
            self.state = AssistState.READY
            self.assist_started_at_s = None
            return 0.0

        if self.assist_started_at_s is None:
            self.assist_started_at_s = now_s
        elif now_s - self.assist_started_at_s > self.config.max_assist_duration_s:
            self.trip(AssistFault.ASSIST_TIMEOUT)
            return 0.0

        self.state = AssistState.ASSISTING
        return _clamp(requested, 0.0, self.config.max_assist_command)


@dataclass
class FingerModel:
    """Small second-order model of normalized drive and finger extension."""

    position_deg: float = 0.0
    velocity_dps: float = 0.0
    drive_acceleration_dps2: float = 1600.0
    spring_per_s2: float = 20.0
    damping_per_s: float = 18.0
    max_position_deg: float = 60.0

    def step(self, normalized_drive: float, dt_s: float) -> None:
        acceleration = (
            self.drive_acceleration_dps2 * _clamp(normalized_drive, 0.0, 1.0)
            - self.spring_per_s2 * self.position_deg
            - self.damping_per_s * self.velocity_dps
        )
        self.velocity_dps += acceleration * dt_s
        self.position_deg += self.velocity_dps * dt_s
        if self.position_deg <= 0.0:
            self.position_deg = 0.0
            self.velocity_dps = max(0.0, self.velocity_dps)
        elif self.position_deg >= self.max_position_deg:
            self.position_deg = self.max_position_deg
            self.velocity_dps = min(0.0, self.velocity_dps)


def intended_activation(timestamp_s: float, config: RehabConfig) -> float:
    """Reference voluntary activation envelope for a finger extension attempt."""

    ramp_s = 0.28
    release_s = 0.34
    if timestamp_s < config.intent_onset_s:
        return 0.0
    if timestamp_s < config.intent_onset_s + ramp_s:
        return _smoothstep((timestamp_s - config.intent_onset_s) / ramp_s)
    if timestamp_s < config.intent_release_s:
        return 1.0
    if timestamp_s < config.intent_release_s + release_s:
        return 1.0 - _smoothstep(
            (timestamp_s - config.intent_release_s) / release_s
        )
    return 0.0


def impaired_activation(timestamp_s: float, config: RehabConfig) -> float:
    """Illustrative weak, delayed, variable activation—not a patient model."""

    delayed = intended_activation(timestamp_s - 0.12, config)
    if delayed <= 0.0:
        return 0.0
    fatigue = 1.0 - 0.20 * _clamp(
        (timestamp_s - 1.30) / max(config.intent_release_s - 1.30, 0.1),
        0.0,
        1.0,
    )
    variability = 0.82 + 0.18 * math.sin(2.0 * math.pi * 1.35 * timestamp_s)
    dropout = 0.32 if 2.08 <= timestamp_s <= 2.24 else 1.0
    return 0.38 * delayed * fatigue * variability * dropout


def _synthetic_emg(
    timestamp_s: float,
    activation: float,
    rng: random.Random,
    phase: tuple[float, float, float],
    baseline_noise: float,
) -> float:
    carrier = (
        0.62 * math.sin(2.0 * math.pi * 43.0 * timestamp_s + phase[0])
        + 0.31 * math.sin(2.0 * math.pi * 71.0 * timestamp_s + phase[1])
        + 0.18 * math.sin(2.0 * math.pi * 97.0 * timestamp_s + phase[2])
    )
    return (
        activation * (carrier + 0.16 * rng.gauss(0.0, 1.0))
        + baseline_noise * rng.gauss(0.0, 1.0)
    )


def moving_rms(values: list[float], window_samples: int) -> list[float]:
    if window_samples < 1:
        raise ValueError("window_samples must be positive")
    result: list[float] = []
    square_sum = 0.0
    for index, value in enumerate(values):
        square_sum += value * value
        if index >= window_samples:
            expired = values[index - window_samples]
            square_sum -= expired * expired
        count = min(index + 1, window_samples)
        result.append(math.sqrt(max(square_sum, 0.0) / count))
    return result


def generate_emg_signals(
    config: RehabConfig | None = None,
    seed: int = 20260912,
) -> tuple[list[float], list[float], list[float], list[float], list[float]]:
    """Return time, two synthetic raw signals, and their RMS envelopes."""

    config = config or RehabConfig()
    reference_rng = random.Random(seed)
    impaired_rng = random.Random(seed + 1)
    reference_phase = (0.2, 1.1, 2.3)
    impaired_phase = (0.5, 1.5, 2.7)
    count = int(round(config.duration_s * config.sample_rate_hz)) + 1
    times = [index * config.dt_s for index in range(count)]
    reference = [
        _synthetic_emg(
            timestamp,
            0.78 * intended_activation(timestamp, config),
            reference_rng,
            reference_phase,
            0.016,
        )
        for timestamp in times
    ]
    impaired = [
        _synthetic_emg(
            timestamp,
            impaired_activation(timestamp, config),
            impaired_rng,
            impaired_phase,
            0.021,
        )
        for timestamp in times
    ]
    window = max(1, round(config.rms_window_s * config.sample_rate_hz))
    return times, reference, impaired, moving_rms(reference, window), moving_rms(impaired, window)


def run_rehab_simulation(
    config: RehabConfig | None = None,
    seed: int = 20260912,
    invalid_signal_at_s: float | None = None,
    contact_drop_at_s: float | None = None,
    placement_alignment: float = 0.92,
    external_estop_at_s: float | None = None,
) -> list[RehabSample]:
    """Run the complete SYNAPSE -> VECTOR -> KINETIC research loop."""

    config = config or RehabConfig()
    times, reference, impaired, reference_rms, impaired_rms = generate_emg_signals(
        config,
        seed,
    )
    baseline_values = [
        value
        for timestamp, value in zip(times, impaired_rms)
        if timestamp <= config.baseline_end_s
    ]
    baseline_rms = sum(baseline_values) / len(baseline_values)
    estimator = IntentEstimator(config, baseline_rms)
    gate = AssistSafetyGate(config)
    dose_controller = NormalizedDoseController(config)
    electrodes = VirtualElectrodeSetup(placement_alignment=placement_alignment)
    unassisted = FingerModel()
    assisted = FingerModel()
    rows: list[RehabSample] = []

    for index, timestamp in enumerate(times):
        signal_valid = invalid_signal_at_s is None or timestamp < invalid_signal_at_s
        external_estop = (
            external_estop_at_s is not None and timestamp >= external_estop_at_s
        )
        electrode_contact = electrodes.minimum_contact_quality
        if contact_drop_at_s is not None and timestamp >= contact_drop_at_s:
            electrode_contact = 0.40
        confidence, detected = estimator.update(impaired_rms[index], signal_valid)
        target_angle = config.target_extension_deg * intended_activation(timestamp, config)
        tracking_error = max(target_angle - assisted.position_deg, 0.0)
        dose_request = 0.46 + 0.65 * tracking_error / config.target_extension_deg
        authorized_correction = gate.authorize(
            dose_request,
            timestamp,
            confidence,
            detected,
            electrode_contact,
            electrodes.placement_alignment,
            signal_valid,
            external_estop,
        )
        stimulation_command = dose_controller.update(
            0.82 * authorized_correction,
            gate.state is AssistState.ASSISTING,
        )
        kinetic_command = (
            min(config.max_kinetic_command, 0.58 * authorized_correction)
            if gate.state is AssistState.ASSISTING
            else 0.0
        )

        voluntary_drive = impaired_activation(timestamp, config)
        unassisted.step(voluntary_drive, config.dt_s)
        assisted.step(
            voluntary_drive
            + 0.70 * stimulation_command
            + 0.48 * kinetic_command,
            config.dt_s,
        )
        rows.append(
            RehabSample(
                timestamp_s=timestamp,
                reference_emg_norm=reference[index],
                impaired_emg_norm=impaired[index],
                reference_envelope=reference_rms[index],
                impaired_envelope=impaired_rms[index],
                intent_confidence=confidence,
                intent_detected=detected,
                electrode_contact_quality=electrode_contact,
                placement_alignment=electrodes.placement_alignment,
                dose_request_norm=(dose_request if detected else 0.0),
                stimulation_command_norm=stimulation_command,
                kinetic_command_norm=kinetic_command,
                target_angle_deg=target_angle,
                unassisted_angle_deg=unassisted.position_deg,
                assisted_angle_deg=assisted.position_deg,
                safety_state=gate.state,
                fault=gate.latched_fault,
            )
        )
    return rows


def summarize_rehab(rows: list[RehabSample], config: RehabConfig | None = None) -> RehabSummary:
    if not rows:
        raise ValueError("cannot summarize an empty simulation")
    config = config or RehabConfig()
    detected_rows = [row for row in rows if row.intent_detected]
    active_rows = [
        row
        for row in rows
        if config.intent_onset_s + 0.45 <= row.timestamp_s <= config.intent_release_s
    ]
    unassisted_squared = [
        (row.target_angle_deg - row.unassisted_angle_deg) ** 2 for row in active_rows
    ]
    assisted_squared = [
        (row.target_angle_deg - row.assisted_angle_deg) ** 2 for row in active_rows
    ]
    unassisted_rmse = math.sqrt(sum(unassisted_squared) / len(unassisted_squared))
    assisted_rmse = math.sqrt(sum(assisted_squared) / len(assisted_squared))
    reduction = 100.0 * (1.0 - assisted_rmse / unassisted_rmse)
    return RehabSummary(
        intent_detected_at_s=(detected_rows[0].timestamp_s if detected_rows else None),
        peak_confidence=max(row.intent_confidence for row in rows),
        reference_peak_envelope=max(row.reference_envelope for row in rows),
        impaired_peak_envelope=max(row.impaired_envelope for row in rows),
        unassisted_peak_deg=max(row.unassisted_angle_deg for row in rows),
        assisted_peak_deg=max(row.assisted_angle_deg for row in rows),
        unassisted_rmse_deg=unassisted_rmse,
        assisted_rmse_deg=assisted_rmse,
        tracking_error_reduction_pct=reduction,
        final_state=rows[-1].safety_state,
        final_fault=rows[-1].fault,
    )

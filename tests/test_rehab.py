import unittest

from vector_mini.rehab import (
    AssistFault,
    AssistState,
    RehabConfig,
    generate_emg_signals,
    run_rehab_simulation,
    summarize_rehab,
)


class RehabSignalTests(unittest.TestCase):
    def test_signal_generation_is_deterministic(self):
        first = generate_emg_signals(seed=17)
        second = generate_emg_signals(seed=17)
        self.assertEqual(first, second)

    def test_reference_envelope_is_stronger_than_impaired_pattern(self):
        rows = run_rehab_simulation()
        summary = summarize_rehab(rows)
        self.assertGreater(
            summary.reference_peak_envelope,
            1.8 * summary.impaired_peak_envelope,
        )

    def test_personalized_estimator_detects_delayed_residual_intent(self):
        config = RehabConfig()
        summary = summarize_rehab(run_rehab_simulation(config), config)
        self.assertIsNotNone(summary.intent_detected_at_s)
        self.assertGreater(summary.intent_detected_at_s, config.intent_onset_s)
        self.assertLess(summary.intent_detected_at_s, 1.50)
        self.assertGreater(summary.peak_confidence, config.confidence_on)


class RehabSafetyTests(unittest.TestCase):
    def test_outputs_remain_zero_until_intent_is_qualified(self):
        rows = run_rehab_simulation()
        pre_intent = [row for row in rows if not row.intent_detected]
        self.assertTrue(pre_intent)
        self.assertTrue(
            all(row.stimulation_command_norm == 0.0 for row in pre_intent)
        )
        self.assertTrue(all(row.kinetic_command_norm == 0.0 for row in pre_intent))

    def test_normalized_outputs_are_bounded_and_stimulation_ramps_up(self):
        config = RehabConfig()
        rows = run_rehab_simulation(config)
        self.assertTrue(
            all(
                0.0 <= row.stimulation_command_norm <= config.max_stimulation_command
                for row in rows
            )
        )
        self.assertTrue(
            all(
                0.0 <= row.kinetic_command_norm <= config.max_kinetic_command
                for row in rows
            )
        )
        allowed_step = config.max_stimulation_ramp_per_s * config.dt_s + 1e-12
        for previous, current in zip(rows, rows[1:]):
            increase = current.stimulation_command_norm - previous.stimulation_command_norm
            self.assertLessEqual(increase, allowed_step)

    def test_contact_loss_latches_fault_and_zeros_both_outputs(self):
        rows = run_rehab_simulation(contact_drop_at_s=1.80)
        fault_rows = [row for row in rows if row.fault is AssistFault.ELECTRODE_CONTACT]
        self.assertTrue(fault_rows)
        self.assertTrue(all(row.safety_state is AssistState.E_STOP for row in fault_rows))
        self.assertTrue(all(row.stimulation_command_norm == 0.0 for row in fault_rows))
        self.assertTrue(all(row.kinetic_command_norm == 0.0 for row in fault_rows))

    def test_invalid_signal_latches_fault(self):
        rows = run_rehab_simulation(invalid_signal_at_s=1.80)
        self.assertEqual(rows[-1].fault, AssistFault.SIGNAL_INVALID)
        self.assertEqual(rows[-1].stimulation_command_norm, 0.0)
        self.assertEqual(rows[-1].kinetic_command_norm, 0.0)

    def test_invalid_virtual_placement_never_authorizes_output(self):
        rows = run_rehab_simulation(placement_alignment=0.50)
        self.assertEqual(rows[-1].fault, AssistFault.PLACEMENT_INVALID)
        self.assertTrue(all(row.stimulation_command_norm == 0.0 for row in rows))
        self.assertTrue(all(row.kinetic_command_norm == 0.0 for row in rows))

    def test_external_estop_is_immediate_and_latched(self):
        rows = run_rehab_simulation(external_estop_at_s=1.80)
        fault_rows = [row for row in rows if row.timestamp_s >= 1.80]
        self.assertTrue(fault_rows)
        self.assertTrue(
            all(row.fault is AssistFault.EXTERNAL_E_STOP for row in fault_rows)
        )
        self.assertTrue(all(row.stimulation_command_norm == 0.0 for row in fault_rows))
        self.assertTrue(all(row.kinetic_command_norm == 0.0 for row in fault_rows))

    def test_assistance_duration_limit_latches_timeout(self):
        config = RehabConfig(max_assist_duration_s=0.25)
        rows = run_rehab_simulation(config)
        fault_rows = [row for row in rows if row.fault is AssistFault.ASSIST_TIMEOUT]
        self.assertTrue(fault_rows)
        self.assertTrue(all(row.stimulation_command_norm == 0.0 for row in fault_rows))
        self.assertTrue(all(row.kinetic_command_norm == 0.0 for row in fault_rows))


class RehabOutcomeTests(unittest.TestCase):
    def test_hybrid_assistance_improves_simulated_movement_tracking(self):
        summary = summarize_rehab(run_rehab_simulation())
        self.assertGreater(summary.assisted_peak_deg, summary.unassisted_peak_deg + 25.0)
        self.assertLess(summary.assisted_rmse_deg, summary.unassisted_rmse_deg)
        self.assertGreater(summary.tracking_error_reduction_pct, 35.0)
        self.assertEqual(summary.final_fault, AssistFault.NONE)


if __name__ == "__main__":
    unittest.main()

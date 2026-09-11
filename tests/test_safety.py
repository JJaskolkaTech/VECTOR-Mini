import unittest

from vector_mini.models import Fault, Limits, SensorFrame
from vector_mini.safety import SafetyGate


class SafetyGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = SafetyGate(Limits())

    def frame(self, **overrides):
        values = dict(timestamp_s=1.0, position_deg=30.0, velocity_dps=0.0)
        values.update(overrides)
        return SensorFrame(**values)

    def test_nominal_frame_passes(self):
        self.assertEqual(self.gate.evaluate(self.frame(), 1.0, None, False), Fault.NONE)

    def test_stale_sensor_trips_watchdog(self):
        fault = self.gate.evaluate(self.frame(timestamp_s=0.0), 1.0, None, False)
        self.assertEqual(fault, Fault.WATCHDOG_TIMEOUT)
        self.assertEqual(self.gate.command(0.8), 0.0)

    def test_position_limit_is_latched(self):
        self.gate.evaluate(self.frame(position_deg=91.0), 1.0, None, False)
        self.assertTrue(self.gate.locked)
        later = self.gate.evaluate(self.frame(position_deg=30.0), 1.1, None, False)
        self.assertEqual(later, Fault.POSITION_LIMIT)

    def test_manual_reset_only_at_safe_posture(self):
        self.gate.trip(Fault.EXTERNAL_E_STOP)
        self.assertFalse(self.gate.manual_reset(40.0))
        self.assertTrue(self.gate.locked)
        self.assertTrue(self.gate.manual_reset(1.0))
        self.assertFalse(self.gate.locked)

    def test_motor_command_is_bounded(self):
        self.assertEqual(self.gate.command(5.0), 1.0)
        self.assertEqual(self.gate.command(-5.0), -1.0)


if __name__ == "__main__":
    unittest.main()


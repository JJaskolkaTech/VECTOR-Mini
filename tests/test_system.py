import unittest

from vector_mini.models import Command, Fault, State
from vector_mini.scenarios import run_scenario
from vector_mini.system import VectorMiniSystem


class SystemTests(unittest.TestCase):
    def test_timeout_scenario_stops_actuation(self):
        rows = list(run_scenario("timeout"))
        final = rows[-1]
        self.assertEqual(final.state, State.E_STOP)
        self.assertEqual(final.fault, Fault.POSITION_TIMEOUT)
        self.assertEqual(final.motor_command, 0.0)

    def test_watchdog_scenario_stops_actuation(self):
        rows = list(run_scenario("watchdog"))
        self.assertEqual(rows[-1].fault, Fault.WATCHDOG_TIMEOUT)
        self.assertFalse(rows[-1].watchdog_healthy)

    def test_nominal_scenario_avoids_fault(self):
        rows = list(run_scenario("nominal"))
        self.assertTrue(rows)
        self.assertTrue(all(row.fault is Fault.NONE for row in rows))

    def test_external_estop_is_immediate(self):
        system = VectorMiniSystem()
        system.dispatch(Command.E_STOP, 0.0)
        row = system.step(0.0, 0.02)
        self.assertEqual(row.motor_command, 0.0)
        self.assertEqual(row.fault, Fault.EXTERNAL_E_STOP)


if __name__ == "__main__":
    unittest.main()


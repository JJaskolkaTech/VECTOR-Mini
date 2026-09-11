import unittest

from vector_mini.models import Command, State
from vector_mini.state_machine import InvalidTransition, MotionStateMachine


class StateMachineTests(unittest.TestCase):
    def test_nominal_sequence(self):
        fsm = MotionStateMachine()
        expected = [State.ARMING, State.FLEX, State.HOLD, State.EXTEND, State.RESET]
        commands = [Command.ARM, Command.FLEX, Command.HOLD, Command.EXTEND, Command.RESET]
        self.assertEqual([fsm.dispatch(c, i) for i, c in enumerate(commands)], expected)

    def test_estop_from_any_state(self):
        for state in State:
            if state is State.E_STOP:
                continue
            fsm = MotionStateMachine(state=state)
            self.assertEqual(fsm.dispatch(Command.E_STOP, 1.0), State.E_STOP)

    def test_invalid_transition_rejected(self):
        with self.assertRaises(InvalidTransition):
            MotionStateMachine().dispatch(Command.FLEX, 0.0)

    def test_reset_requires_safe_posture(self):
        fsm = MotionStateMachine(state=State.E_STOP)
        with self.assertRaises(InvalidTransition):
            fsm.manual_reset(2.0, mechanism_safe=False)
        self.assertEqual(fsm.manual_reset(2.0, mechanism_safe=True), State.IDLE)


if __name__ == "__main__":
    unittest.main()


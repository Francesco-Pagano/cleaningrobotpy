from unittest import TestCase
from unittest.mock import Mock, patch, call

from defer import return_value

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot, CleaningRobotError


class TestCleaningRobot(TestCase):

    def test_initialize_robot(self):
        system = CleaningRobot()
        system.initialize_robot()
        self.assertEqual(system.robot_status(),"(0,0,N)")

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_greater_than_10(self, mock: Mock, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11
        system.manage_cleaning_system()
        mock.assert_has_calls([call(system.RECHARGE_LED_PIN, GPIO.LOW), call(system.CLEANING_SYSTEM_PIN, GPIO.HIGH)])

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_equal_or_less_than_10(self, mock: Mock, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 9
        system.manage_cleaning_system()
        mock.assert_has_calls([call(system.RECHARGE_LED_PIN, GPIO.HIGH), call(system.CLEANING_SYSTEM_PIN, GPIO.LOW)])

    @patch.object(IBS, "get_charge_left")
    def test_move_forward(self, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11
        system.initialize_robot()
        system.execute_command(system.FORWARD)
        self.assertEqual(system.robot_status(), "(0,1,N)")

    @patch.object(IBS, "get_charge_left")
    def test_move_right(self, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11
        system.initialize_robot()
        system.execute_command(system.RIGHT)
        self.assertEqual(system.robot_status(), "(0,0,E)")

    @patch.object(IBS, "get_charge_left")
    def test_move_left(self, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11
        system.initialize_robot()
        system.execute_command(system.LEFT)
        self.assertEqual(system.robot_status(), "(0,0,W)")

    @patch.object(IBS, "get_charge_left")
    def test_not_move(self, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11
        system.initialize_robot()
        self.assertRaises(CleaningRobotError, system.execute_command, "X")

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "input")
    def test_obstacle_found(self, mock_infrared: Mock, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 11
        mock_infrared.return_value = True
        system.initialize_robot()
        self.assertEqual(system.execute_command(system.FORWARD),"(0,0,N)(0,1)")

    @patch.object(IBS, "get_charge_left")
    def test_charge_left_equal_or_less_than_10(self, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 9
        system.initialize_robot()
        system.pos_x = 1
        system.pos_y = 1
        system.heading = system.N
        system.manage_cleaning_system()
        self.assertEqual(system.execute_command(system.FORWARD),"!(1,1,N)")

    @patch.object(IBS, "get_charge_left")
    @patch.object(CleaningRobot, "change_servo_angle")
    @patch.object(GPIO, "input")
    def test_grab_object(self, mock_infrared: Mock, mock_servo: Mock, mock_ibs: Mock):
        system = CleaningRobot()
        mock_ibs.return_value = 20
        mock_infrared.return_value = True
        system.initialize_robot()
        system.execute_command(system.FORWARD)
        mock_servo.assert_called_with(12)
        self.assertTrue(system.close_arm)


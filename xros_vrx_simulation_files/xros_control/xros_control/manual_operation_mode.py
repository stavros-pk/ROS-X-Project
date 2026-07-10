#!/usr/bin/env python3
"""
Operation mode node.

Tracks the vessel's current manual operation mode (normal / crab / bow) and
publishes changes to /manual_mode. Mode can be changed via:
    - joystick buttons (1/2/3, gated by button 0 being released)
    - a String command on /operation_cmd
    - the 'operation_mode' ROS parameter
"""

from enum import Enum

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String
from sensor_msgs.msg import Joy


class Mode(Enum):
    NORMAL = "normal"
    CRAB = "crab"
    BOW = "bow"

    @classmethod
    def from_str(cls, s: str):
        """Case-insensitive lookup; raises ValueError on bad input."""
        for member in cls:
            if member.value == s.lower():
                return member
        valid = [m.value for m in cls]
        raise ValueError(f"Unknown mode '{s}'. Valid modes: {valid}")


class OperationModeNode(Node):

    def __init__(self):
        super().__init__("manual_operation_mode")

        self._mode = Mode.NORMAL
        self.status = ""

        self.declare_parameter('operation_mode', Mode.NORMAL.value)
        self.add_on_set_parameters_callback(self._on_param_change)

        self._status_pub = self.create_publisher(String, '/manual_mode', 10)

        self.operation_change_cmd = self.create_subscription(
            Joy, 'joy', self._mode_change_cmd_cb, 10)
        self.create_subscription(
            String, '/operation_cmd', self._mode_cmd_cb, 10)
        self.robot_status = self.create_subscription(
            String, '/robot_status', self._status, 10)

        self.get_logger().info("Mode Node started - mode: NORMAL")

    # =====================================================================
    # Mode transition
    # =====================================================================

    def _set_mode(self, new_mode: Mode) -> str:
        """Central transition function; returns a human-readable message."""
        if new_mode == self._mode:
            return f"Already in {new_mode.value} mode."

        old = self._mode
        self._mode = new_mode
        msg = f"Mode change: {old.value} \u2192 {new_mode.value}"

        status_msg = String()
        status_msg.data = self._mode.value
        self._status_pub.publish(status_msg)

        self.get_logger().info(msg)
        return msg

    # =====================================================================
    # Input callbacks
    # =====================================================================

    def _mode_change_cmd_cb(self, msg: Joy):
        
        if self.status == 'manual':
            self.buttons = msg.buttons

            if self.buttons[1] == 1 and self.buttons[0] == 0:
                self._set_mode(Mode.from_str('normal'))
            elif self.buttons[2] == 1 and self.buttons[0] == 0:
                self._set_mode(Mode.from_str('crab'))
            elif self.buttons[3] == 1 and self.buttons[0] == 0:
                self._set_mode(Mode.from_str('bow'))
            else:
                pass
        else:
            pass
            

    def _mode_cmd_cb(self, msg: String):
        """Switch mode via /operation_cmd topic (std_msgs/String)."""
        try:
            new_mode = Mode.from_str(msg.data)
            self._set_mode(new_mode)
        except ValueError as e:
            self.get_logger().warn(str(e))

    def _status(self, msg):
        self.status = msg.data

    def _on_param_change(self, params):
        """Handle: ros2 param set /manual_operation_mode operation_mode <value>"""
        for p in params:
            if p.name == "operation_mode" and p.type_ == Parameter.Type.STRING:
                try:
                    new_mode = Mode.from_str(p.value)
                    result_msg = self._set_mode(new_mode)
                    return SetParametersResult(successful=True, reason=result_msg)
                except ValueError as e:
                    return SetParametersResult(successful=False, reason=str(e))

        return SetParametersResult(successful=True)


# =========================================================================
# Entry point
# =========================================================================

def main(args=None):
    rclpy.init(args=args)
    node = OperationModeNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

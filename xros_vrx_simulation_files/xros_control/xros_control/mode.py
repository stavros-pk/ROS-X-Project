#!/usr/bin/env python3
"""
Mode selector node.

Tracks the vessel's top-level operating mode (idle / manual / autonomous /
emergency) and publishes changes to /robot_status. Mode can be changed via:
    - joystick button combinations (see _mode_change_cmd_cb)
    - a String command on /mode_cmd
    - the 'mode' ROS parameter

EMERGENCY can only be exited by explicitly switching to IDLE.
"""

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String
from sensor_msgs.msg import Joy
from enum import Enum


class Mode(Enum):
    IDLE = "idle"
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"
    EMERGENCY = "emergency"

    @classmethod
    def from_str(cls, s: str):
        """Case-insensitive lookup; raises ValueError on bad input."""
        for member in cls:
            if member.value == s.lower():
                return member

        valid = [m.value for m in cls]
        raise ValueError(f"Unknown mode '{s}'. Valid modes: {valid}")


class ModeSelectorNode(Node):

    def __init__(self):
        super().__init__("mode_selector")

        # --- Internal state ---
        self._mode = Mode.IDLE
        self.prev_button_0 = 0  # tracks previous frame's button[0] state, for edge detection

        self.declare_parameter("mode", Mode.IDLE.value)
        self.add_on_set_parameters_callback(self._on_param_change)

        self._status_pub = self.create_publisher(String, "/robot_status", 10)

        self.operation_change_cmd = self.create_subscription(Joy, 'joy', self._mode_change_cmd_cb, 10)
        self.create_subscription(String, "/mode_cmd", self._mode_cmd_cb, 10)

        self.get_logger().info("Mode Node started - mode: IDLE")

    # =====================================================================
    # Mode transition
    # =====================================================================

    def _set_mode(self, new_mode: Mode) -> str:
        """Central transition function; returns a human-readable message."""
        if new_mode == self._mode:
            return f"Already in {new_mode.value} mode."

        # Guard: cannot leave EMERGENCY without explicit clear to IDLE
        if self._mode == Mode.EMERGENCY and new_mode != Mode.IDLE:
            return (
                "EMERGENCY active - clear it first by switching to IDLE.\n"
                "  ros2 service call /set_mode/idle std_srvs/srv/Trigger {}"
            )

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
        self.buttons = msg.buttons

        if self.buttons[0] == self.prev_button_0:
            # button[0] held steady across frames — used as a "sustained
            # press" gate for the safety-critical transitions.
            if self.buttons[0] == 1 and self.buttons[1] == 1:
                self._set_mode(Mode.from_str('emergency'))
            elif self.buttons[2] == 1 and self.buttons[0] == 1:
                self._set_mode(Mode.from_str('idle'))

        elif self.buttons[0] == 1 and self.buttons[1] == 0 and self._mode.value == "idle":
            # button[0] rising edge — cycles through the normal modes
            self._set_mode(Mode.from_str('manual'))

        elif self.buttons[0] == 1 and self.buttons[1] == 0 and self._mode.value == "manual":
            self._set_mode(Mode.from_str('autonomous'))

        elif self.buttons[0] == 1 and self.buttons[1] == 0 and self._mode.value == "autonomous":
            self._set_mode(Mode.from_str('manual'))

        else:
            pass

        self.prev_button_0 = self.buttons[0]

    def _mode_cmd_cb(self, msg: String):
        """Switch mode via /mode_cmd topic (std_msgs/String)."""
        try:
            new_mode = Mode.from_str(msg.data)
            self._set_mode(new_mode)
        except ValueError as e:
            self.get_logger().warn(str(e))

    def _on_param_change(self, params):
        """Handle: ros2 param set /mode_selector mode <value>"""
        for p in params:
            if p.name == "mode" and p.type_ == Parameter.Type.STRING:
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
    node = ModeSelectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
 

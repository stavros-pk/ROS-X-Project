#!/usr/bin/env python3
"""
Vessel control node.

Reads joystick input and vessel status/mode to drive thrusters in one of
several manual control modes (normal, bow, crab). In "crab" mode, heading
is held/adjusted via a PID setpoint published to an external PID controller
node, whose output (pid_effort) is applied to the bow thruster.
"""

import math

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy, Imu
from std_msgs.msg import Float64, String
from data_interfaces.msg import Actuators


# --- Tunable constants -------------------------------------------------
NORMAL_THRUST_SCALE = 2000.0
CRAB_THRUST_SCALE = 500.0
JOYSTICK_DEADZONE = 0.2
CRAB_MOVE_DEADZONE = 0.5
HEADING_NUDGE_DEGREES_PER_TICK = 1.0
LEFT_POS_SCALE = 60 * math.pi / 360


class Data_receiver(Node):

    def __init__(self):
        super().__init__('serial_control')

        # --- State -----------------------------------------------------
        self._mode = "idle"
        self._manual_mode = "normal"
        self.pointer = 0
        self._pid_effort = 0.0
        self._current_heading_deg = None  # set once IMU data arrives

        # --- Subscribers -------------------------------------------------
        self.subscriber = self.create_subscription(
            Joy, 'joy', self.commands, 10)
        self.manual_mode = self.create_subscription(
            String, '/manual_mode', self._manual_commands_cb, 10)
        self.mode = self.create_subscription(
            String, '/robot_status', self._status_cb, 10)
        self.setpoint = self.create_subscription(
            Imu, '/wamv/sensors/imu/imu/data', self._heading_cb, 10)
        self.effort = self.create_subscription(
            Float64, 'pid_effort', self._effort_cb, 10)

        # --- Publishers --------------------------------------------------
        self.left_thrust = self.create_publisher(
            Float64, '/wamv/thrusters/left/thrust', 10)
        self.right_thrust = self.create_publisher(
            Float64, '/wamv/thrusters/right/thrust', 10)
        self.bow_thrust = self.create_publisher(
            Float64, '/wamv/thrusters/bow/thrust', 10)
        self.left_pos = self.create_publisher(
            Float64, '/wamv/thrusters/left/pos', 10)
        self.right_pos = self.create_publisher(
            Float64, '/wamv/thrusters/right/pos', 10)
        self.setpoint_pid = self.create_publisher(
            Float64, 'desired_heading', 10)
        self.current_heading = self.create_publisher(
            Float64, 'current_heading', 10)

    # =====================================================================
    # Main joystick callback — dispatches to the active mode
    # =====================================================================
    def commands(self, msg):
        try:
            self.axes = msg.axes

            if self._mode == "manual" and self._manual_mode == "normal":
                self._handle_normal_mode()

            elif self._mode == "manual" and self._manual_mode == "bow":
                self._handle_bow_mode()

            elif self._mode == "manual" and self._manual_mode == "crab":
                self._handle_crab_mode()

            elif self._mode == "idle" or self._mode == "emergency":
                self._handle_idle_or_emergency()

            else:
                pass

        except KeyboardInterrupt:
            self.get_logger().info("Control Node Terminated")

    # --- Mode handlers -------------------------------------------------

    def _handle_normal_mode(self):
        if self.pointer == 1:
            self.pointer = 0

        thrust = self.axes[3] * NORMAL_THRUST_SCALE
        self._publish(self.left_thrust, thrust)
        self._publish(self.right_thrust, thrust)

        pos = -self.axes[0] * LEFT_POS_SCALE
        self._publish(self.left_pos, pos)
        self._publish(self.right_pos, pos)

        self._publish(self.bow_thrust, 0.0)

    def _handle_bow_mode(self):
        if self.pointer == 1:
            self.pointer = 0

        self._publish(self.left_thrust, 0.0)
        self._publish(self.right_thrust, 0.0)
        self._publish(self.left_pos, 0.0)
        self._publish(self.right_pos, 0.0)

        self._publish(self.bow_thrust, self.axes[3] * NORMAL_THRUST_SCALE)

    def _handle_crab_mode(self):
        # On entering crab mode: initialize the PID setpoint to the
        # vessel's current heading, so it holds position rather than
        # snapping to some stale target.
        if self.pointer == 0:
            if self._current_heading_deg is None:
                self.get_logger().warn(
                    'Entering crab mode before IMU data received; '
                    'deferring setpoint initialization.'
                )
                return

            self.pin_point = Float64()
            self.pin_point.data = self._current_heading_deg
            self.setpoint_pid.publish(self.pin_point)
            self.pointer = 1

        # Nudge the desired heading with the twist axis
        if abs(self.axes[2]) >= JOYSTICK_DEADZONE:
            self.pin_point.data += HEADING_NUDGE_DEGREES_PER_TICK * self.axes[2]
            self.pin_point.data = self._wrap_degrees(self.pin_point.data)
            self.setpoint_pid.publish(self.pin_point)

        # Always publish fresh heading feedback to the PID, every cycle
        heading_msg = Float64()
        heading_msg.data = self._current_heading_deg
        self.current_heading.publish(heading_msg)

        # Translational movement (strafe) direction
        if abs(self.axes[0]) < JOYSTICK_DEADZONE and abs(self.axes[1]) < JOYSTICK_DEADZONE:
            angle = 0.0
        else:
            angle = math.atan2(self.axes[0], self.axes[1])

        magnitude = math.sqrt(self.axes[0] ** 2 + self.axes[1] ** 2)
        if abs(self.axes[0]) < CRAB_MOVE_DEADZONE and abs(self.axes[1]) < CRAB_MOVE_DEADZONE:
            thrust = 0.0
        else:
            thrust = magnitude * CRAB_THRUST_SCALE

        self._publish(self.left_thrust, thrust)
        self._publish(self.right_thrust, thrust)
        self._publish(self.left_pos, angle)
        self._publish(self.right_pos, angle)

        # NOTE: bow thrust is NOT published here — it's driven directly
        # from _effort_cb() as soon as a new PID output arrives, so it
        # updates at the PID's own rate instead of the joystick's rate.

    def _handle_idle_or_emergency(self):
        if self.pointer == 1:
            self.pointer = 0

        self._publish(self.left_thrust, 0.0)
        self._publish(self.right_thrust, 0.0)
        self._publish(self.left_pos, 0.0)
        self._publish(self.right_pos, 0.0)
        self._publish(self.bow_thrust, 0.0)

    # =====================================================================
    # Subscription callbacks
    # =====================================================================

    def _heading_cb(self, msg: Imu):
        """Updates current vessel heading (degrees) from IMU orientation."""
        q = msg.orientation
        self._current_heading_deg = self._quaternion_to_yaw_degrees(
            q.x, q.y, q.z, q.w
        )

    def _status_cb(self, msg: String):
        self._mode = msg.data

    def _manual_commands_cb(self, msg: String):
        self._manual_mode = msg.data

    def _effort_cb(self, msg: Float64):
        """Applies new PID output to the bow thruster immediately,
        independent of the joystick callback rate."""
        self._pid_effort = msg.data
        if self._mode == "manual" and self._manual_mode == "crab":
            self._publish(self.bow_thrust, self._pid_effort)

    # =====================================================================
    # Helpers
    # =====================================================================

    @staticmethod
    def _publish(publisher, value: float):
        msg = Float64()
        msg.data = value
        publisher.publish(msg)

    @staticmethod
    def _wrap_degrees(angle_deg: float) -> float:
        """Wraps an angle to the range [-180, 180]."""
        if angle_deg > 180:
            return angle_deg - 360
        if angle_deg < -180:
            return angle_deg + 360
        return angle_deg

    @staticmethod
    def _quaternion_to_yaw_degrees(x: float, y: float, z: float, w: float) -> float:
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw_rad = math.atan2(siny_cosp, cosy_cosp)
        return math.degrees(yaw_rad)


def main(args=None):
    rclpy.init(args=args)
    data_receiver = Data_receiver()

    try:
        rclpy.spin(data_receiver)
    except KeyboardInterrupt:
        pass
    finally:
        data_receiver.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
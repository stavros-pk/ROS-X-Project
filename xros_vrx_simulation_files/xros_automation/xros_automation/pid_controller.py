#!/usr/bin/env python3
"""
Generic PID controller node for ROS 2.

Subscribes to:
    setpoint  (std_msgs/Float64) - desired target value (e.g. heading, degrees)
    feedback  (std_msgs/Float64) - current measured value

Publishes:
    control_effort (std_msgs/Float64) - PID output

Parameters (all dynamically reconfigurable at runtime):
    kp, ki, kd       - PID gains
    min_output       - output clamp minimum
    max_output       - output clamp maximum
    max_integral     - anti-windup clamp on the integral term
    angular          - if true, treats setpoint/feedback as degrees on a
                        circle and wraps error to [-180, 180]
"""

import time

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import Float64


class PIDControllerNode(Node):

    def __init__(self):
        super().__init__('pid')

        # --- Declare parameters with defaults ---
        self.declare_parameter('kp', 80.0)
        self.declare_parameter('ki', 0.0)
        self.declare_parameter('kd', 0.0)
        self.declare_parameter('min_output', -2000.0)
        self.declare_parameter('max_output', +2000.0)
        self.declare_parameter('max_integral', 100.0)
        self.declare_parameter('angular', True)

        # --- Cache parameter values ---
        self.kp = self.get_parameter('kp').value
        self.ki = self.get_parameter('ki').value
        self.kd = self.get_parameter('kd').value
        self.min_output = self.get_parameter('min_output').value
        self.max_output = self.get_parameter('max_output').value
        self.max_integral = self.get_parameter('max_integral').value
        self.angular = self.get_parameter('angular').value

        # --- Internal PID state ---
        self.setpoint = 0.0
        self.current_value = 0.0
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None
        self.have_feedback = False

        # --- React to live parameter changes ---
        self.add_on_set_parameters_callback(self.parameter_callback)

        # --- Subscribers ---
        self.setpoint_sub = self.create_subscription(
            Float64, 'setpoint', self.setpoint_callback, 10
        )
        self.feedback_sub = self.create_subscription(
            Float64, 'feedback', self.feedback_callback, 10
        )

        # --- Publisher ---
        self.effort_pub = self.create_publisher(Float64, 'control_effort', 10)

        # --- Control loop timer (50 Hz) ---
        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info(
            f'PID controller started (kp={self.kp}, ki={self.ki}, kd={self.kd}, '
            f'angular={self.angular})'
        )

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'kp':
                self.kp = param.value
            elif param.name == 'ki':
                self.ki = param.value
            elif param.name == 'kd':
                self.kd = param.value
            elif param.name == 'min_output':
                self.min_output = param.value
            elif param.name == 'max_output':
                self.max_output = param.value
            elif param.name == 'max_integral':
                self.max_integral = param.value
            elif param.name == 'angular':
                self.angular = param.value

            self.get_logger().info(f'{param.name} updated to {param.value}')

        # Reset integral term whenever gains change to avoid a sudden kick
        self.integral = 0.0

        return SetParametersResult(successful=True)

    def setpoint_callback(self, msg: Float64):
        self.setpoint = msg.data

    def feedback_callback(self, msg: Float64):
        self.current_value = msg.data
        self.have_feedback = True

    def control_loop(self):
        if not self.have_feedback:
            return  # nothing to control against yet

        now = time.monotonic()
        if self.prev_time is None:
            self.prev_time = now
            return  # need at least one prior sample for dt

        dt = now - self.prev_time
        if dt <= 0.0:
            return

        error = self.setpoint - self.current_value

        # For angular quantities (e.g. heading in degrees), wrap the error
        # itself to [-180, 180] so the controller always takes the shortest
        # path — this handles every case, not just values near +-90.
        if self.angular:
            error = (error + 180) % 360 - 180

        # Proportional
        p_term = self.kp * error

        # Integral (with anti-windup clamp)
        self.integral += error * dt
        self.integral = max(-self.max_integral, min(self.max_integral, self.integral))
        i_term = self.ki * self.integral

        # Derivative
        derivative = (error - self.prev_error) / dt
        d_term = self.kd * derivative

        output = p_term + i_term + d_term
        output = max(self.min_output, min(self.max_output, output))

        msg = Float64()
        msg.data = output
        self.effort_pub.publish(msg)

        self.prev_error = error
        self.prev_time = now


def main(args=None):
    rclpy.init(args=args)
    node = PIDControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
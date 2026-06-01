import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
import time
from data_interfaces.action import RudderControl


class RudderControlServer(Node):

    def __init__(self):
        super().__init__('rudder_control_server')
        self._action_server = ActionServer(
            self,
            RudderControl,
            'rudder_control',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        feedback_msg = RudderControl.Feedback()
        feedback_msg.current_angle = 0

        #Code here
        for i in range(feedback_msg.current_angle, goal_handle.request.ordered_angle):
            if feedback_msg.current_angle < goal_handle.request.ordered_angle:
                feedback_msg.current_angle = feedback_msg.current_angle + 1
            else:
                feedback_msg.current_angle = feedback_msg.current_angle - 1
            self.get_logger().info('Feedback: {0}'.format(feedback_msg.current_angle))
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.01)

        goal_handle.succeed()
        result = RudderControl.Result()
        result.final_angle = feedback_msg.current_angle
        return result


def main(args=None):
    rclpy.init(args=args)

    rudder_control_server = RudderControlServer()

    rclpy.spin(rudder_control_server)


if __name__ == '__main__':
    main()

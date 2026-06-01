import rclpy
from rclpy.node import Node
from data_interfaces.msg import Rudder

from RPi import GPIO
import time

DEFAULT_PIN_IN1 = 7
DEFAULT_PIN_IN2 = 11
DEFAULT_PIN_IN3 = 13
DEFAULT_PIN_IN4 = 15
DEFAULT_MOTOR = "PORT"

class RudderController(Node):
    def __init__(self):

        super.__init__("rudder")

        self.declare_parameter("pin_in1",DEFAULT_PIN_IN1)
        self.declare_parameter("pin_in2",DEFAULT_PIN_IN2)
        self.declare_parameter("pin_in3",DEFAULT_PIN_IN3)
        self.declare_parameter("pin_in4",DEFAULT_PIN_IN4)
        self.declare_parameter("motor",DEFAULT_MOTOR)

        control_pin_in1 = self.get_parameter("pin_in1").value
        control_pin_in2 = self.get_parameter("pin_in2").value
        control_pin_in3 = self.get_parameter("pin_in3").value
        control_pin_in4 = self.get_parameter("pin_in4").value
        motor = self.get_parameter("motor").value

        self.get_logger().info("Setting up pins...")

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(control_pin_in1,GPIO.OUT)
        GPIO.setup(control_pin_in2,GPIO.OUT)
        GPIO.setup(control_pin_in3,GPIO.OUT)
        GPIO.setup(control_pin_in4,GPIO.OUT)

        GPIO.output(control_pin_in1,0)
        GPIO.output(control_pin_in2,0)
        GPIO.output(control_pin_in3,0)
        GPIO.output(control_pin_in4,0)

        self.get_logger().info("Subscribing to topics...")
        self.line_sub_ = self.create_subscription(
            Rudder,
            "cmd_rudder", 
            self._cmd_callback, 
            10
        )
        self.get_logger().info("CMD Completed")

        def _cmd_callback(self, msg: Rudder):
            if motor == "PORT":
                rudder = msg.angle_p
            elif motor == "STARBOARD":
                rudder = msg.angle_s
            angle_stepper(rudder)


        def angle_stepper(self, angle):
            control_pins = [control_pin_in1, control_pin_in2, control_pin_in3, control_pin_in4]
            halfstep_seq = [
                [1,0,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,1,1,0],
                [0,0,1,0],
                [0,0,1,1],
                [0,0,0,1],
                [1,0,0,1],
            ]
            steps = angle*512/360
            for i in range(steps):
                for halfstep in range(8):
                    for pin in range(4):
                        GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
                    time.sleep(0.001)

def main(args=None):
    rclpy.init(args=args)

    movement = RudderController()

    rclpy.spin(movement)

    movement.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
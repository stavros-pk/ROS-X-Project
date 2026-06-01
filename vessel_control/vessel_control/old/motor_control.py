import rclpy
from rclpy.node import Node
from data_interfaces.msg import MotorControl

from RPi import GPIO
import time

DEFAULT_PIN_A_FWD = 17 #Port motor
DEFAULT_PIN_A_REV = 22 #Port motor
DEFAULT_PIN_B_FWD = 23 #Starboard motor
DEFAULT_PIN_B_REV = 24 #Starboard motor
PWM0 = 12
PWM1 = 13
DEFAULT_PWM_FREQUENCY = 2000 # Hz
DEFAULT_FULL_SPEED_DUTY_CYCLE = 100 # %

class MotorController(Node):
    def __init__(self):

        super().__init__('motor_control')

        self.declare_parameter("motor_a_forward_pin",DEFAULT_PIN_A_FWD)
        self.declare_parameter("motor_a_reverse_pin",DEFAULT_PIN_A_REV)
        self.declare_parameter("motor_b_forward_pin",DEFAULT_PIN_B_FWD)
        self.declare_parameter("motor_b_reverse_pin",DEFAULT_PIN_B_REV)
        self.declare_parameter("motor_a_pwm_pin",PWM0)
        self.declare_parameter("motor_b_pwm_pin",PWM1)
        self.declare_parameter("pwm_frequency",DEFAULT_PWM_FREQUENCY)
        self.declare_parameter("max_duty_cycle",DEFAULT_FULL_SPEED_DUTY_CYCLE)
        motor_a_pin_fwd = self.get_parameter("motor_a_forward_pin").value
        motor_a_pin_rev = self.get_parameter("motor_a_reverse_pin").value
        motor_b_pin_fwd = self.get_parameter("motor_b_forward_pin").value
        motor_b_pin_rev = self.get_parameter("motor_b_reverse_pin").value
        motor_a = self.get_parameter("motor_a_pwm_pin").value
        motor_b = self.get_parameter("motor_b_pwm_pin").value

        pwm_frequency = self.get_parameter("pwm_frequency").value
        self._full_speed_duty_cycle = self.get_parameter("max_duty_cycle").value

        self.get_logger().info("Setting up motor pins...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(motor_a_pin_fwd,GPIO.OUT)
        GPIO.setup(motor_a_pin_rev,GPIO.OUT)
        GPIO.setup(motor_b_pin_fwd,GPIO.OUT)
        GPIO.setup(motor_b_pin_rev,GPIO.OUT)
        GPIO.setup(motor_a,GPIO.OUT)
        GPIO.setup(motor_b,GPIO.OUT)
        self._motor_a = GPIO.PWM(motor_a, pwm_frequency)
        self._motor_b = GPIO.PWM(motor_b, pwm_frequency)
        self._motor_a_pin_fwd = GPIO.output(motor_a_pin_fwd, False)
        self._motor_a_pin_rev = GPIO.output(motor_a_pin_rev, False)
        self._motor_b_pin_fwd = GPIO.output(motor_b_pin_fwd, False)
        self._motor_b_pin_rev = GPIO.output(motor_b_pin_rev, False)

        self._motor_a.start(0)
        self._motor_b.start(0)

        self.get_logger().info("Subscribing to topics...")
        self.line_sub_ = self.create_subscription(
            MotorControl,
            "cmd_motor", 
            self._cmd_callback, 
            10
        )
        self.get_logger().info("CMD Completed")

    def _cmd_callback(self, msg: MotorControl):
        
        try:
            speed_a = min(100, abs(msg.thrust_p)*self._full_speed_duty_cycle)
            speed_b = min(100, abs(msg.thrust_s)*self._full_speed_duty_cycle)
            
            self._motor_a.ChangeDutyCycle(speed_a)
            self._motor_b.ChangeDutyCycle(speed_b)
            if msg.thrust_p >= 0:
                GPIO.output(17, GPIO.HIGH)
                GPIO.output(22, GPIO.LOW)
            else:
                GPIO.output(17, GPIO.LOW)
                GPIO.output(22, GPIO.HIGH)
            
            if msg.thrust_s >= 0:
                GPIO.output(23, GPIO.HIGH)
                GPIO.output(24, GPIO.LOW)
            else:
                GPIO.output(23, GPIO.LOW)
                GPIO.output(24, GPIO.HIGH)
        except KeyboardInterrupt:
            self._motor_a.ChangeDutyCycle(0)
            self._motor_b.ChangeDutyCycle(0)
        
        

def main(args=None):
    rclpy.init(args=args)

    movement = MotorController()

    rclpy.spin(movement)

    movement.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()



        




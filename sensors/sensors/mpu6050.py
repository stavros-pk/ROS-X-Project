import rclpy
from rclpy.node import Node
import adafruit_mpu6050
import board
from data_interfaces.msg import MpuData


class MPU6050(Node):

    def __init__(self):
        super().__init__('mpu6050')
        self.publisher_ = self.create_publisher(MpuData, 'mpu_data', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.sensor_data)
        i2c = board.I2C()
        self.sensor = adafruit_mpu6050.MPU6050(i2c,104)
        

    def sensor_data(self):
        msg = MpuData()

        try:
            msg.acc_x = self.sensor.acceleration[0]
            msg.acc_y = self.sensor.acceleration[1]
            msg.acc_z = self.sensor.acceleration[2]
            msg.gyro_x = self.sensor.gyro[0]
            msg.gyro_y = self.sensor.gyro[1]
            msg.gyro_z = self.sensor.gyro[2]

            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: %f, %f, %f' % (msg.acc_x, msg.acc_y, msg.acc_z))
        except RuntimeError as error:
            msg.data = 'Err Measurement'
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: "%s"' % msg.data)
            pass

        except KeyboardInterrupt:
            self.get_logger().info('Program Terminated')
            
        
def main(args=None):
    rclpy.init(args=args)

    mpu_sensor = MPU6050()

    rclpy.spin(mpu_sensor)

    mpu_sensor.destroy_node()
    rclpy.shutdown

if __name__ == '__main__':
    main()
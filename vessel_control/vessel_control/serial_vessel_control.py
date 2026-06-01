import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import serial

s = serial.Serial('/dev/ttyACM0',115200)

class Data_receiver(Node):

    def __init__(self):
        super().__init__('serial_control')
        self.subscriber = self.create_subscription(Joy, '/joy', self.commands, 10)
        self.subscriber

    def commands(self,msg):
        
        try:
            self.axes = msg.axes
            self.buttons = msg.buttons
            self.get_logger().info(f"Axes: {[round(a,2) for a in self.axes]}")
            self.thrust_1 = self.axes[3]*225
            self.thrust_2 = self.axes[3]*225
            self.step_1 = self.axes[0]*60
            self.step_2 = self.axes[0]*60

            string = ["P1:"+str(round(self.thrust_1,0))+"\n","P2:"+str(round(self.thrust_2,0))+"\n","R1:"+str(round(self.step_1,0))+"\n","R2:"+str(round(self.step_2,0))+"\n"]

            for i in range(4):
                s.write(string[i].encode("utf-8"))
        
        except KeyboardInterrupt:
            self.get_logger().info("Control Node Terminated")



        

        


def main(args=None):
    rclpy.init(args=args)
    data_receiver = Data_receiver()

    try:
        rclpy.spin(data_receiver)
    except KeyboardInterrupt:
        pass
    finally:
        data_receiver.destroy_node
        rclpy.shutdown

if __name__ == '__main__':
    main()

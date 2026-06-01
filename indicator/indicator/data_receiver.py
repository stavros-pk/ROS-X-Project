import rclpy
from rclpy.node import Node
from data_interfaces.msg import Coordinates

class Data_receiver(Node):

    def __init__(self):
        super().__init__('data_receiver')
        self.subscriber = self.create_subscription(Coordinates, 'gps_data', self.read_data, 10)
        self.subscriber

    def read_data(self,msg):
        self.get_logger().info("%f, %f" % (msg.lon, msg.lat))

def main(args=None):
    rclpy.init(args=args)
    data_receiver = Data_receiver()

    rclpy.spin(data_receiver)
    data_receiver.destroy_node
    rclpy.shutdown

if __name__ == '__main__':
    main()

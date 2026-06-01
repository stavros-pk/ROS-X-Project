#!/usr/bin/env python3
"""
ROS2 Publisher — DHT11 Temperature & Humidity Sensor (GPIO)
Package : sensors   <-- replace with your package name
Node    : dht

The DHT11 uses a single-wire protocol and is read through a GPIO pin.
This script uses the 'adafruit-circuitpython-dht' library.

Dependencies:
    pip install adafruit-circuitpython-dht
    sudo apt install libgpiod2
    sudo apt install ros-<distro>-sensor-msgs

Topics published:
    /dht_data/temp  (data_interfaces/Dht)
    /dht_data/humi     (data_interfaces/Dht)

Note:
    The DHT11 is limited to one reading every ~2 seconds. Publishing faster
    than 0.5 Hz will return stale or failed readings. The default here is
    0.5 Hz (one read every 2 s). For continuous high-rate data consider
    upgrading to a DHT22 or an SHT31 over I²C.

Usage:
    ros2 run my_robot_sensors dht_sensor
"""

import rclpy
from rclpy.node import Node
import adafruit_dht
import board
from data_interfaces.msg import Dht

# ── Configuration ────────────────────────────────────────────────────────────
# GPIO pin connected to the DATA line of the DHT11.
# Use board.D<number> notation, e.g. board.D4 for GPIO4.
DHT_PIN      = board.D4      # ← change to your wiring

PUBLISH_HZ   = 0.5           # 0.5 Hz = one reading every 2 s (DHT11 limit)


# Sensor variance estimates (approximate for DHT11 at room temperature)
TEMP_VARIANCE = 4.0   # ±2 °C accuracy → variance ≈ 4 °C²
# ─────────────────────────────────────────────────────────────────────────────

class DHT(Node):

    def __init__(self):
        super().__init__('dht')
        self.publisher_ = self.create_publisher(Dht, 'dht_data', 10)
        timer_period = 2.0

        try:
            # use_pulseio=False is safer on modern Pi kernels that lack PulseIO
            self.sensor = adafruit_dht.DHT11(DHT_PIN)#,use_pulseio=False)
            self.get_logger().info(f'DHT11 initialised on pin {DHT_PIN}')
        except Exception as exc:
            self.get_logger().fatal(f'Cannot initialise DHT11: {exc}')
            raise SystemExit(1) from exc

        self.timer = self.create_timer(timer_period, self.sensor_data)
        

    def sensor_data(self):
        msg = Dht()
         
        try:
            temp = self.sensor.temperature
            humi = self.sensor.humidity
            
            if temp is not None and humi is not None:
                msg.temp = float(temp) 
                msg.humi = int(humi)
                self.publisher_.publish(msg)
                self.get_logger().info('Publishing: "%d,%d"' % (msg.temp,msg.humi))  
            else:
                pass
                    
        except RuntimeError as error:
            
            self.get_logger().warn('Publishing: Error')
            
            pass

        except Exception as error:
            self.sensor.exit()
            raise error

    def destroy_node(self):
        try:
            self._dht.exit()
            self.get_logger().info('DHT11 released')
        except Exception:
            pass
        super().destroy_node()

        
def main(args=None):
    rclpy.init(args=args)

    dht_sensor = DHT()

    try:
        rclpy.spin(dht_sensor)
    except KeyboardInterrupt:
        pass
    finally:
        dht_sensor.destroy_node()
        rclpy.shutdown

if __name__ == '__main__':
    main()
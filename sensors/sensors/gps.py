#!/usr/bin/env python3
"""
ROS2 Publisher — GPS NEO-M6 (via UART/Serial)
Package : sensors
Node    : gps_neo_m6

Dependencies:
    pip install pyserial pynmea2

Topic published:
    /gps/gps_data   (sensor_msgs/Coordinates)

Usage:
    ros2 run gps_neo_m6
"""

import rclpy
from rclpy.node import Node
from data_interfaces.msg import Coordinates

import serial
import pynmea2


# ── Configuration ────────────────────────────────────────────────────────────
SERIAL_PORT  = '/dev/ttyAMA0'   # adjust if using USB (/dev/ttyUSB0)
BAUD_RATE    = 9600
PUBLISH_HZ   = 1.0              # publish rate in Hz (GPS typically 1 Hz)
TOPIC        = '/gps/fix'
# ─────────────────────────────────────────────────────────────────────────────


class GpsNeoM6(Node):

    def __init__(self):
        super().__init__('gps_neo_m6')

        self._pub = self.create_publisher(Coordinates, "gps_data", 10)

        # Open serial port once; raise early if the port is unavailable.
        try:
            self._serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2.0)
            self.get_logger().info(
                f'Opened serial port {SERIAL_PORT} @ {BAUD_RATE} baud'
            )
        except serial.SerialException as exc:
            self.get_logger().fatal(f'Cannot open serial port: {exc}')
            raise SystemExit(1) from exc

        self._timer = self.create_timer(1.0 / PUBLISH_HZ, self._timer_cb)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _read_gga(self) -> pynmea2.GGA | None:
        """Read lines from the serial buffer until a valid GGA sentence is found."""
        for _ in range(30):          # try up to 30 lines before giving up
            try:
                raw = self._serial.readline().decode('ascii', errors='replace').strip()
                
            except serial.SerialException as exc:
                self.get_logger().error(f'Serial read error: {exc}')
                return None

            if not raw.startswith('$'):
                continue

            try:
                msg = pynmea2.parse(raw)
                if isinstance(msg, pynmea2.GGA):
                    return msg
            except pynmea2.ParseError:
                pass

        return None

    # ── Timer callback ────────────────────────────────────────────────────────

    def _timer_cb(self):
        gga = self._read_gga()

        if gga is None:
            self.get_logger().warn('No valid GGA sentence received — skipping publish')
            return

        msg = Coordinates()
        #msg.time   = self.get_clock().now().to_msg()

        # NavSatStatus
        #status = NavSatStatus()
        #if gga.gps_qual == 0:
        #    status.status = NavSatStatus.STATUS_NO_FIX
        #elif gga.gps_qual == 2:
        #    status.status = NavSatStatus.STATUS_GBAS_FIX   # DGPS
        #else:
        #    status.status = NavSatStatus.STATUS_FIX
        #status.service = NavSatStatus.SERVICE_GPS
        #msg.status = status

        msg.lat  = gga.latitude   if gga.latitude  else float('nan')
        msg.lon = gga.longitude  if gga.longitude else float('nan')
        #msg.altitude  = float(gga.altitude) if gga.altitude else float('nan')

        # Covariance — approximation based on HDOP
        # A proper implementation would use HDOP from the sentence.
        #msg.position_covariance_type = Coordinates.COVARIANCE_TYPE_UNKNOWN

        self._pub.publish(msg)
        self.get_logger().info(
            f'Published GPS fix: lat={msg.lat:.6f}  '
            f'lon={msg.lon:.6f}'
        )

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def destroy_node(self):
        if self._serial.is_open:
            self._serial.close()
            self.get_logger().info('Serial port closed')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GpsNeoM6()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
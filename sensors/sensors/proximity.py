#!/usr/bin/env python3
"""
ROS2 Publisher — 5x VL53L0X Time-of-Flight Proximity Sensors (I²C)
Package : sensors
Node    : tof_publisher

All five VL53L0X sensors share the same I²C bus.  Because every sensor
boots at the same default address (0x29), the XSHUT pin of each sensor
must be pulled LOW to disable all others, then each one is powered up
individually and re-addressed to a unique I²C address before the next
sensor is enabled.

Wiring (example — adapt GPIO numbers to your board):
    Sensor        XSHUT GPIO   I²C address assigned
    ─────────────────────────────────────────────────
    front_c       17           0x30
    front_left    27           0x31
    front_right   22           0x32
    back_left     23           0x33
    back_right    24           0x34

Dependencies:
    pip install adafruit-circuitpython-vl53l0x adafruit-blinka

    I²C must be enabled on your host (raspi-config → Interfaces → I2C).

Topics published:
    proximity_data   (data_interfaces/ProximityData)

Usage:
    ros2 run sensors proximity_sensors
"""

import math
import rclpy
import board
import busio
import digitalio

from rclpy.node import Node
from adafruit_vl53l0x import VL53L0X
from data_interfaces.msg import ProximityData

# ── Publish rate ──────────────────────────────────────────────────────────────
PUBLISH_HZ = 10.0
TOPIC      = 'proximity_data'

# ── Sensor definitions ────────────────────────────────────────────────────────
# Each entry: (field_name_on_msg, XSHUT_board_pin, unique_i2c_address)
#
# Use the board.Dxx constants that match your physical wiring.
# The addresses must all be different and must not be 0x29
# (the factory default — we leave 0x29 free so a cold-booted sensor
# never clashes with an already-configured one).
SENSOR_CONFIGS = [
    ('front_c',     board.D17, 0x30),
    ('front_left',  board.D27, 0x31),
    ('front_right', board.D22, 0x32),
    ('back_left',   board.D23, 0x33),
    ('back_right',  board.D24, 0x34),
]
# ─────────────────────────────────────────────────────────────────────────────


def _make_xshut(pin) -> digitalio.DigitalInOut:
    """Return a DigitalInOut output pin, initially LOW (sensor disabled)."""
    xshut = digitalio.DigitalInOut(pin)
    xshut.direction = digitalio.Direction.OUTPUT
    xshut.value = False   # hold sensor in reset
    return xshut


class ProximitySensorNode(Node):

    def __init__(self):
        super().__init__('tof_vl53l0k')

        self._pub = self.create_publisher(ProximityData, TOPIC, 10)

        # Each element: {'field': str, 'sensor': VL53L0X | None, 'xshut': DigitalInOut}
        self._sensors: list[dict] = []

        self._init_sensors()

        active = sum(1 for s in self._sensors if s['sensor'] is not None)
        self.get_logger().info(
            f'{active}/{len(SENSOR_CONFIGS)} VL53L0X sensor(s) initialised successfully.'
        )

        self._timer = self.create_timer(1.0 / PUBLISH_HZ, self._timer_cb)

    # ── Sensor initialisation ─────────────────────────────────────────────────

    def _init_sensors(self):
        """
        Boot each sensor one at a time using XSHUT, then re-address it.

        Strategy
        ────────
        1. Pull ALL XSHUT pins LOW  →  every sensor is in hardware reset.
        2. For each sensor in turn:
             a. Drive its XSHUT HIGH  →  sensor boots at 0x29.
             b. Re-address it to its unique address.
             c. If anything fails, leave sensor=None (reads will yield NaN).
        """
        i2c = busio.I2C(board.SCL, board.SDA)

        # Step 1 — disable every sensor
        xshut_pins = []
        for (field, pin, _addr) in SENSOR_CONFIGS:
            xshut_pins.append(_make_xshut(pin))

        # Step 2 — enable and address each sensor individually
        for idx, (field, _pin, address) in enumerate(SENSOR_CONFIGS):
            xshut = xshut_pins[idx]
            xshut.value = True          # release reset → sensor boots at 0x29

            try:
                sensor = VL53L0X(i2c)           # connects at default 0x29
                sensor.set_address(address)     # move to unique address
                self.get_logger().info(
                    f'[{field}] VL53L0X ready @ 0x{address:02X}'
                )
            except Exception as exc:
                self.get_logger().error(
                    f'[{field}] Failed to initialise VL53L0X @ 0x{address:02X}: {exc}'
                )
                sensor = None

            self._sensors.append({
                'field':  field,
                'sensor': sensor,
                'xshut':  xshut,
            })

    # ── Timer callback ────────────────────────────────────────────────────────

    def _timer_cb(self):
        msg = ProximityData()

        # Default every field to NaN; only overwrite on a successful read
        for s in self._sensors:
            setattr(msg, s['field'], math.nan)

        for s in self._sensors:
            field  = s['field']
            sensor = s['sensor']

            if sensor is None:
                # Sensor was never initialised — NaN already set
                continue

            try:
                distance_mm = sensor.range          # Adafruit property (mm, int)

                if distance_mm <= 0:
                    # Sensor returned an invalid / out-of-range reading
                    self.get_logger().warn(
                        f'[{field}] Invalid reading ({distance_mm} mm) — publishing NaN'
                    )
                    # Leave as NaN
                else:
                    setattr(msg, field, distance_mm / 1000.0)   # mm → m

            except Exception as exc:
                self.get_logger().error(
                    f'[{field}] Ranging error: {exc} — publishing NaN'
                )
                # Leave as NaN

        self._pub.publish(msg)

        # Debug log — one compact line per cycle
        parts = [
            f'{s["field"]}={getattr(msg, s["field"]) * 1000:.0f}mm'
            if not math.isnan(getattr(msg, s['field']))
            else f'{s["field"]}=NaN'
            for s in self._sensors
        ]
        self.get_logger().debug('ToF: ' + '  '.join(parts))

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def destroy_node(self):
        for s in self._sensors:
            try:
                if s['sensor'] is not None:
                    pass   # adafruit_vl53l0x has no explicit close/stop method
                s['xshut'].value = False    # put sensor back in reset
                s['xshut'].deinit()
            except Exception:
                pass
        self.get_logger().info('All VL53L0X sensors shut down.')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ProximitySensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
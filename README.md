# ROS-X

### Autonomous Surface Vessel Platform based on ROS 2

<p align="center">
<img width="1447" height="722" alt="Screenshot (73)" src="https://github.com/user-attachments/assets/8533ab65-cb60-4fed-9f17-22c604282bcf" />
</p>

> ROS-X is an experimental Autonomous Surface Vessel (ASV) developed using ROS 2 and inspired by the Ulstein X-BOW® hull concept. The project's goal is to achieve autonomous navigation, remote teleoperation, sensor fusion, mission planning and real-time vessel monitoring through a custom web dashboard. The project started in March of 2026 and it is the continuation of the Suomenlinna Project.

---

## Table of Contents

- [Overview](#overview)
- [Vessel Design](#vessel-design)
- [System Architecture](#system-architecture)
- [ROS Graph](#ros-graph)
- [Sensor Suite](#sensor-suite)
- [Vessel Control](#vessel-control)
- [Remote Teleoperation](#remote-teleoperation)
- [Dashboard](#dashboard)
- [Hardware](#hardware)
- [Roadmap](#roadmap)

---

## Overview

ROS-X is a modular research platform for autonomous maritime systems. The vessel integrates navigation sensors, environmental monitoring, propulsion control and remote operation into a distributed ROS 2 architecture running on a Raspberry Pi.

**Current objectives:**

- Autonomous waypoint navigation
- Sensor fusion and localization
- Remote vessel monitoring
- Human-in-the-loop teleoperation
- Mission planning and execution

---

## Vessel Design

The hull is inspired by the **Ulstein X-BOW®** concept. Unlike conventional bow geometries, the X-BOW extends forward below the waterline, allowing the vessel to pierce waves rather than climb over them. This results in improved stability, reduced slamming, better sensor performance and more predictable motion in rough seas.

### Hull

<img width="1447" height="722" alt="Hull isometric" src="https://github.com/user-attachments/assets/a57675d0-178d-48ff-9591-ef3cf4e1fa2f" />
<img width="1507" height="687" alt="Hull side" src="https://github.com/user-attachments/assets/949acdf6-3ff7-4dff-9298-b34e189528cf" />

### Bow Thruster Assembly

The vessel includes an independently controlled bow thruster used for low-speed manoeuvring, station keeping, docking assistance and future autonomous positioning algorithms.

<img width="958" height="646" alt="Thruster front" src="https://github.com/user-attachments/assets/927a7e64-3f8c-47ba-a909-36b8f3d30400" /> | <img width="757" height="698" alt="Thruster iso" src="https://github.com/user-attachments/assets/2923d22d-d1de-4160-9dc1-82e5a118dfe5" /> | <img width="1163" height="674" alt="Thruster rear" src="https://github.com/user-attachments/assets/4d0db25b-a041-4e67-b738-5c0489174c65" />

### Azipod Propulsion *(In Development)*

A future objective of ROS-X is the integration of an **Azipod-inspired propulsion system**, providing the vessel with full-vector thrust capabilities and significantly improved manoeuvrability.

Unlike conventional fixed propulsion arrangements, an azimuthing propulsion unit can rotate around its vertical axis, allowing thrust to be directed in any desired heading. This capability enables precise low-speed control, enhanced station-keeping performance, and greater effectiveness when operating in confined or complex environments such as marinas, harbours, and docking areas.

The design philosophy follows the propulsion concepts developed during the **Suomenlinna Project**, adapting them to the ROS-X platform and its autonomous navigation framework.

Planned capabilities include:

* 360° thrust vectoring
* Dynamic positioning support
* Improved autonomous docking
* Enhanced station-keeping performance
* Reduced turning radius
* Integration with future navigation and control algorithms

The Azipod system remains under active development and will form a key component of the vessel's long-term autonomy and manoeuvring capabilities.

---

## System Architecture

```text
                    ┌─────────────────────┐
                    │   Web Dashboard     │
                    │ Mission Planning    │
                    │ Telemetry & Control │
                    └──────────┬──────────┘
                               │ WiFi / Ethernet
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │                    Raspberry Pi 4                    │
    │                      ROS 2 Core                      │
    ├──────────────────────────────────────────────────────┤
    │  Sensors Layer                                       │
    │  gps_neo_m6    ──► gps_data                          │
    │  mpu6050       ──► imu_data                          │
    │  magnetometer  ──► heading_data                      │
    │  dht           ──► environment_data                  │
    │  tof_vl53l0x   ──► proximity_data                    │
    ├──────────────────────────────────────────────────────┤
    │  Control Layer                                       │
    │  joy_node      ──► /joy                              │
    │  serial_control──► propulsion commands               │
    ├──────────────────────────────────────────────────────┤
    │  Mission Layer (In Progress)                         │
    │  waypoint_manager                                    │
    │  navigation_logic                                    │
    │  obstacle_avoidance                                  │
    └──────────────────────┬───────────────────────────────┘
                           │ Serial
                           ▼
                  ┌─────────────────┐
                  │  Arduino / ESC  │
                  └────────┬────────┘
                           ▼
                    Motors / Rudders
```

---

## ROS Graph

```text
gps_neo_m6  ──► gps_data  ──────────────► data_receiver
mpu6050     ──► imu_data
magnetometer──► heading_data
dht         ──► environment_data
tof_vl53l0x ──► proximity_data

joy_node ──► /joy ──► serial_control ──► Port Motor
                                    ──► Starboard Motor
                                    ──► Port Angle
                                    ──► Starboard Angle

```

---

## Sensor Suite

### GPS — u-blox NEO-M6

Provides latitude, longitude, UTC time and position fix.

### IMU — MPU6050

Provides 3-axis acceleration and angular velocity.

### Magnetometer

Provides magnetic heading and compass bearing. Intended for EKF fusion with the MPU6050 for robust yaw estimation.

    ---

## Vessel Control

The propulsion system uses azipod thrust. The control node receives joystick commands and converts them into port/starboard thrust and angle, transmitted over serial to the motor controller hardware.

---

## Remote Teleoperation

The vessel can be controlled remotely via SSH using a joystick with the assistance of the teleoperation feature of ROS2 suite.

```text
Joystick ──► joy_node ──► teleop_twist_joy ──► serial_control ──► Vessel
```

```bash
ros2 run joy joy_node
ros2 run teleop_twist_joy teleop_node
ros2 run vessel_control serial_vessel_control
```

---

## Dashboard

A custom web dashboard developed with AI assistance provides a modern interface for vessel monitoring and mission execution.

| Module | Features |
|---|---|
| **Camera** | Live stream, snapshot, stream control |
| **Navigation** | Directional, heading & speed control, telemetry |
| **Mission Planner** | Interactive map, waypoint management, route generation, upload & execute |
| **System Monitor** | CPU, memory, temperature, uptime |
| **Marine Awareness** | Harbours, marinas, anchorages, lighthouses, nav markers |

<img width="1076" height="700" alt="Dashboard navigation" src="https://github.com/user-attachments/assets/bfb46761-fcd0-4984-96b2-d4b8ef635e97" />
<img width="1076" height="701" alt="Dashboard mission" src="https://github.com/user-attachments/assets/84af7bf8-4962-4a49-8552-31d1ddeb562d" />
<img width="1076" height="841" alt="Dashboard system" src="https://github.com/user-attachments/assets/11f9ef42-1aa9-4c2b-afdd-c2f80532a582" />

---

## Hardware
The hardware used in this project can be summarized in the following table:

| Component | Description |
|---|---|
| Raspberry Pi 4 | Onboard compute |
| NEO-M6 | GPS positioning |
| MPU6050 | IMU (accel + gyro) |
| Magnetometer | Heading / compass |
| DHT11 | Temperature & humidity |
| 5× VL53L0X | Time-of-Flight proximity |
| Bow Thruster | Low-speed manoeuvring |
| Dual Azipod Thrusters | Directional control |
| ESC / Motor Controller | Propulsion interface |
| USB Joystick | Manual teleoperation |

---

## Roadmap
### Sensors
- [x] GPS publisher (NEO-M6, UART/NMEA)
- [x] IMU publisher (MPU-6050, I²C)
- [x] Temperature & humidity publisher (DHT11)
- [x] 5-zone ToF proximity publisher (VL53L0X)

### Actuators
- [x] Stepper motor control
- [x] DC motor control

### Teleoperation
- [x] Serial propulsion control (joystick → ESC)
- [x] Remote joystick teleoperation via SSH
- [x] Web dashboard (telemetry + command)

### Navigation
- [ ] Waypoint navigation
- [ ] Path planning
- [ ] Autonomous return-to-home

### Localisation
- [ ] EKF sensor fusion (GPS + IMU + Magnetometer)
- [ ] Heading stabilisation

### Perception
- [ ] Obstacle avoidance
- [ ] Camera-based detection
- [ ] Shoreline awareness

### Operations
- [ ] Dashboard ↔ ROS integration
- [ ] Cloud telemetry
- [ ] Remote fleet monitoring

---

## Project Status

🚧 **Active Development**

ROS-X is being developed as a research platform for autonomous maritime systems, combining ROS 2, embedded hardware and modern web technologies into a single cohesive architecture.

*"Building the future of autonomous maritime robotics, one node at a time."* ⚓🤖

---

### Acknowledgements

- ROS 2 Community
- OpenStreetMap & OpenSeaMap
- Ulstein Group for the X-BOW® inspiration

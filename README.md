# ROS-X

### Autonomous Surface Vessel Platform based on ROS 2

<p align="center">

<img width="1447" height="722" alt="Screenshot (73)" src="https://github.com/user-attachments/assets/8533ab65-cb60-4fed-9f17-22c604282bcf" />

</p>

> ROS-X is an experimental Autonomous Surface Vessel (ASV) developed using ROS 2 and inspired by the Ulstein X-BOW® hull concept. The project combines autonomous navigation, remote teleoperation, sensor fusion, mission planning and real-time vessel monitoring through a custom web dashboard.

---

## Overview

ROS-X was created as a modular research platform for autonomous maritime systems.

The vessel integrates navigation sensors, environmental monitoring, propulsion control and remote operation into a distributed ROS 2 architecture running on a Raspberry Pi.

Current objectives include:

* Autonomous waypoint navigation
* Sensor fusion and localization
* Remote vessel monitoring
* Human-in-the-loop teleoperation
* Mission planning and execution

---

## Vessel Design

The hull design is inspired by the **Ulstein X-BOW®** concept.

Unlike conventional bow geometries, the X-BOW extends forward below the waterline, allowing the vessel to pierce waves rather than climb over them. This results in:

* Improved stability
* Reduced slamming
* Better sensor performance
* Increased comfort during long missions
* More predictable motion in rough seas

### Hull

<img width="1447" height="722" alt="Screenshot (73)" src="https://github.com/user-attachments/assets/a57675d0-178d-48ff-9591-ef3cf4e1fa2f" />
<img width="1507" height="687" alt="Screenshot (72)" src="https://github.com/user-attachments/assets/949acdf6-3ff7-4dff-9298-b34e189528cf" />

### Bow Thruster Assembly

The vessel includes an independently controlled bow thruster used for:

* Low-speed manoeuvring
* Station keeping
* Docking assistance
* Future autonomous positioning algorithms

<img width="958" height="646" alt="Screenshot (75)" src="https://github.com/user-attachments/assets/927a7e64-3f8c-47ba-a909-36b8f3d30400" />
<img width="757" height="698" alt="Screenshot (74)" src="https://github.com/user-attachments/assets/2923d22d-d1de-4160-9dc1-82e5a118dfe5" />
<img width="1163" height="674" alt="Screenshot (76)" src="https://github.com/user-attachments/assets/4d0db25b-a041-4e67-b738-5c0489174c65" />


### Azipod Propulsion

In Progress ...

---

# System Architecture

```text
                          ┌─────────────────────┐
                          │   Web Dashboard     │
                          │ Mission Planning    │
                          │ Telemetry & Control │
                          └──────────┬──────────┘
                                     │
                                     │
                         WiFi / Ethernet
                                     │
                                     ▼

        ┌───────────────────────────────────────────────────────┐
        │                  Raspberry Pi 4                       │
        │                    ROS 2 Core                         │
        ├───────────────────────────────────────────────────────┤
        │                                                       │
        │  Sensors Layer                                        │
        │                                                       │
        │  gps_neo_m6        ──► gps_data                       │
        │  mpu6050           ──► imu_data                       │
        │  magnetometer      ──► heading_data                   │
        │  dht               ──► environment_data               │
        │  tof_vl53l0x       ──► proximity_data                 │
        │                                                       │
        │                                                       │
        │  Control Layer                                        │
        │                                                       │
        │  joy_node          ──► /joy                           │
        │  serial_control    ──► propulsion commands            │
        │  rudder_control    ──► rudder commands                │
        │                                                       │
        │                                                       │
        │  Mission Layer (In progress)                          │
        │                                                       │
        │  waypoint manager                                     │
        │  navigation logic                                     │
        │  obstacle avoidance (future)                          │
        │                                                       │
        └───────────────────────────────────────────────────────┘
                                   │
                                   │ Serial
                                   ▼
                          ┌─────────────────┐
                          │ Arduino / ESC   │
                          └────────┬────────┘
                                   │
                                   ▼
                            Motors / Rudders
```

---

# ROS Graph

```text
gps_neo_m6
    │
    ▼
gps_data ───────────────► data_receiver

mpu6050
    │<img width="1447" height="722" alt="Screenshot (73)" src="https://github.com/user-attachments/assets/414c5fcb-ee87-482e-b37a-bc3ed6388378" />

    ▼
imu_data

magnetometer
    │
    ▼
heading_data

dht
    │
    ▼
environment_data

tof_vl53l0x
    │
    ▼
proximity_data


joy_node
    │
    ▼
/joy
    │
    ▼
serial_control
    │
    ├────► Port Motor
    │
    ├────► Starboard Motor
    │
    ├────► Port Rudder
    │
    └────► Starboard Rudder


cmd_rudder
    │
    ▼
rudder_control
```

---

# Sensor Suite

## GPS

**u-blox NEO-M6**

Provides:

* Latitude
* Longitude
* UTC time
* Position fix

Topic:

```bash
gps_data
```

---

## IMU

**MPU6050**

Provides:

* Acceleration
* Angular velocity

Topic:

```bash
mpu_data
```

---

## Magnetometer

**3-axis digital compass**

Provides:

* Magnetic heading
* Compass bearing
* Future yaw correction for navigation

Topic:

```bash
magnetometer_data
```

This node is intended to complement the MPU6050 and will later be fused through an EKF for robust heading estimation.

---

## Environmental Sensor

**DHT11**

Provides:

* Temperature
* Humidity

Topic:

```bash
dht_data
```

---

## Obstacle Detection

**5 × VL53L0X Time-of-Flight Sensors**

Coverage:

```text
           Front Left
                \
                 \
Front Center ---- Vessel ---- Front Right

Back Left ------------------- Back Right
```

Topic:

```bash
proximity_data
```

---

# Vessel Control

The propulsion system uses differential thrust together with dual rudders.

The control node receives joystick commands and converts them into:

* Port motor thrust
* Starboard motor thrust
* Port rudder angle
* Starboard rudder angle

Commands are transmitted through a serial interface to the motor controller hardware.

---

# Remote Teleoperation

The vessel can be controlled remotely through SSH using a USB joystick.

```text
Joystick
    │
    ▼
joy_node
    │
    ▼
teleop_twist_joy
    │
    ▼
serial_control
    │
    ▼
Vessel
```

Launch:

```bash
ros2 run joy joy_node

ros2 run teleop_twist_joy teleop_node

ros2 run vessel_control serial_vessel_control
```

---

# Dashboard

A custom AI-assisted dashboard provides a modern interface for vessel monitoring and mission execution.

### Features

#### Camera

* Live video stream
* Snapshot capture
* Stream control

#### Navigation

* Directional control
* Heading control
* Speed control
* Telemetry display

#### Mission Planner

* Interactive map
* Waypoint management
* Route generation
* Mission upload
* Mission execution

#### System Monitoring

* CPU usage
* Memory usage
* Temperature
* Uptime

#### Marine Awareness

* Harbours
* Marinas
* Anchorages
* Lighthouses
* Navigation markers

### Dashboard Preview

<!-- DASHBOARD SCREENSHOT HERE -->

![Dashboard](docs/images/dashboard.jpg)

---

# Launch

Launch the complete ROS-X stack:

```bash
ros2 launch vessel_control ros_project.launch.py
```

---

# Hardware

* Raspberry Pi 4
* NEO-M6 GPS
* MPU6050 IMU
* Magnetometer
* DHT11
* 5× VL53L0X ToF Sensors
* Bow Thruster
* Dual Rudders
* ESC / Motor Controller
* USB Joystick

---

# Roadmap

## Navigation

* [ ] Waypoint navigation
* [ ] Path planning
* [ ] Autonomous return-to-home

## Localization

* [ ] EKF sensor fusion
* [ ] GPS + IMU + Magnetometer fusion
* [ ] Heading stabilization

## Perception

* [ ] Obstacle avoidance
* [ ] Camera-based detection
* [ ] Shoreline awareness

## Operations

* [ ] Dashboard ↔ ROS integration
* [ ] Cloud telemetry
* [ ] Remote fleet monitoring

---

# Project Status

🚧 Active Development

ROS-X is currently being developed as a research platform for autonomous maritime systems, combining ROS 2, embedded systems and modern web technologies into a single autonomous vessel architecture.

"Building the future of autonomous maritime robotics, one node at a time." ⚓🤖

---

### Acknowledgements

* ROS 2 Community
* OpenStreetMap
* OpenSeaMap
* Ulstein Group for the X-BOW® inspiration




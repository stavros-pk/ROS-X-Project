# ROS-X

### Autonomous Surface Vessel Platform based on ROS 2

<p align="center">
<img width="1428" height="616" alt="Screenshot from 2026-07-10 13-35-27" src="https://github.com/user-attachments/assets/02675355-e42e-47bf-9745-0f35752f7269" />
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

<img width="1428" height="616" alt="Screenshot from 2026-07-10 13-35-27" src="https://github.com/user-attachments/assets/842354e1-d316-49e9-abd0-392318b24c66" />
<img width="1401" height="492" alt="Screenshot from 2026-07-10 13-34-37" src="https://github.com/user-attachments/assets/6d015b4d-611e-4637-aa8f-853b66eb3fb6" />

### Bow Thruster Assembly

The vessel includes an independently controlled bow thruster used for low-speed manoeuvring, station keeping, docking assistance and future autonomous positioning algorithms.
<div align="center">
<table>
  <tr>
    <td align="center"><img width="958" height="646" alt="Thruster front" src="https://github.com/user-attachments/assets/927a7e64-3f8c-47ba-a909-36b8f3d30400" /></td>
    <td align="center"><img width="757" height="698" alt="Thruster iso" src="https://github.com/user-attachments/assets/2923d22d-d1de-4160-9dc1-82e5a118dfe5" /></td>
    <td align="center"><img width="1163" height="674" alt="Thruster rear" src="https://github.com/user-attachments/assets/4d0db25b-a041-4e67-b738-5c0489174c65" /></td>
  </tr>
  <tr>
    <td colspan="3" align="center"><b>Bow Thruster 3D Design</b></td>
  </tr>
</table>
</div>




### Azipod Propulsion *(In Development)*

A future objective of ROS-X is the integration of an **Azipod-inspired propulsion system**, providing the vessel with full-vector thrust capabilities and significantly improved manoeuvrability.

Unlike conventional fixed propulsion arrangements, an azimuthing propulsion unit can rotate around its vertical axis, allowing thrust to be directed in any desired heading. This capability enables precise low-speed control, enhanced station-keeping performance, and greater effectiveness when operating in confined or complex environments such as marinas, harbours, and docking areas.

The design philosophy follows the propulsion concepts developed during the **Suomenlinna Project**, adapting them to the ROS-X platform and its autonomous navigation framework.

<table>
  <tr>
    <td align="center"><img width="606" height="598" alt="Screenshot from 2026-07-10 13-39-05" src="https://github.com/user-attachments/assets/183e11bb-12d4-46d7-808f-011fc7526a3a" /></td>
    <td align="center"><img width="469" height="780" alt="Screenshot from 2026-07-10 13-38-33" src="https://github.com/user-attachments/assets/1927d7d1-0356-4049-aace-fa2ec7300c73" /></td>
    <td align="center"><img width="884" height="710" alt="Screenshot from 2026-07-10 13-40-56" src="https://github.com/user-attachments/assets/e8ffa7f2-7152-48e3-b6a4-083005f9b26e" /></td>
  </tr>
  <tr>
    <td colspan="3" align="center"><b>Azipod Propulsion 3D Design</b></td>
  </tr>
</table>

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
 
Development has moved into **simulation-first validation** using the [VRX](https://github.com/osrf/vrx) (Virtual RobotX) environment on Gazebo. A custom WAM-V model was built for this — starting from the stock dual-thruster hull and adding an **independently controlled bow thruster**, matching the physical bow thruster design shown above, so the exact same control and navigation stack developed here can later be transferred to the real vessel with minimal changes.

<div align="center">
<table>
  <tr>
    <td align="center"><img width="891" height="545" alt="Screenshot from 2026-07-10 14-16-39" src="https://github.com/user-attachments/assets/a2dee705-4e33-447c-8118-a9ea173d0b45" />
</td>
  </tr>
  <tr>
    <td colspan="3" align="center"><b>VRX Simulation</b></td>
  </tr>
</table>
</div>
 
The ROS 2 stack is organized into four packages:
 
| Package | Responsibility |
|---|---|
| `xros_control` | Mode/state management and joystick-driven vessel control |
| `xros_automation` | Heading-hold PID controller |
| `xros_path_planning` | Waypoint route and Point-of-Interest (POI) services |
| `data_interfaces` | Shared custom messages and services (`Actuators`, `Poi`, waypoint/POI services) |
 
```text
                    ┌──────────────────────┐
                    │   Web Dashboard      │
                    │  Mission Planning    │
                    │ Telemetry & Control  │
                    └──────────┬───────────┘
                               │ WiFi / Ethernet
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │                    ROS 2 Core                        │
    ├──────────────────────────────────────────────────────┤
    │  Input Layer                                         │
    │  joy_node          ──► /xros/joy                     │
    ├──────────────────────────────────────────────────────┤
    │  Mode Layer (xros_control)                           │
    │  mode_selector         ──► /robot_status             │
    │  manual_operation_mode ──► /manual_mode              │
    │  vessel_control        ──► thrust / position commands│
    ├──────────────────────────────────────────────────────┤
    │  Automation Layer (xros_automation)                  │
    │  heading_pid  (setpoint, feedback) ──► control_effort│
    ├──────────────────────────────────────────────────────┤
    │  Mission Layer (xros_path_planning)                  │
    │  waypoint_handler  ──► route / current waypoint (srv)│
    │  poi_handler        ──► points of interest (srv)     │
    └──────────────────────────┬───────────────────────────┘
                               │
                               ▼
                   Simulated / Physical Vessel
              (VRX WAM-V in Gazebo, or Arduino/ESC)
```
 
---
 
## ROS Graph
 
The current graph, as brought up by `xros_bringup.launch.py`:
 
<div align="center">
<table>
  <tr>
    <td align="center"><img width="1544" height="536" alt="Screenshot from 2026-07-10 14-20-44" src="https://github.com/user-attachments/assets/5887b750-d3ef-420a-ae6f-f8a7e47824c0" />
</td>
  </tr>
  <tr>
    <td colspan="3" align="center"><b>RQT Graph</b></td>
  </tr>
</table>
</div>
 
`vessel_control` is the central node: it reads joystick axes, the active operating mode, and live IMU heading, then drives the three thrusters directly for **normal** and **bow** manual modes, or hands heading control to `heading_pid` for the **crab** mode, applying its output (`pid_effort`) to the bow thruster for automatic heading hold.
 
---
 
## Sensor Suite
 
For simulation development, sensor feedback is provided by the VRX/Gazebo WAM-V model rather than physical hardware:
 
### IMU (simulated)
 
Publishes orientation on `/wamv/sensors/imu/imu/data`. `vessel_control` converts the quaternion to a yaw heading in degrees, which serves as the live feedback signal for the heading-hold PID controller.
 
### GPS (simulated)
 
Provides latitude/longitude used by the waypoint and POI services (`xros_path_planning`) for route definition and mission points.
 
### Camera & Lidar (simulated)
 
A forward-facing camera and a 16-beam lidar are configured on the simulated vessel (`my_vessel_config`), reserved for the upcoming obstacle avoidance and perception work on the roadmap.
 
The physical sensor suite (GPS NEO-M6, MPU6050 IMU, magnetometer, DHT11, VL53L0X) listed under [Hardware](#hardware) remains the target sensor set for the physical vessel; the simulation environment mirrors this set so that control and navigation logic developed against it transfers directly once the physical build is ready for integration testing.
 
---
 
## Vessel Control
 
The vessel is controlled through three independently driven thrusters — **left**, **right**, and an **independently steerable bow thruster** — coordinated by `vessel_control` based on the active operating mode:
 
| Mode | Behaviour |
|---|---|
| **Normal** | Differential left/right thrust and steering from joystick axes; bow thruster idle |
| **Bow** | Bow thruster driven directly from joystick throttle for close-quarters manoeuvring |
| **Crab** | Left/right thrusters provide lateral (strafe) thrust; the bow thruster is driven automatically by `heading_pid` to hold or nudge heading, decoupling heading control from lateral movement |
 
Mode selection is layered:
- **`mode_selector`** — top-level state: `idle → manual → autonomous`, plus a dedicated `emergency` state that can only be cleared by explicitly returning to `idle`
- **`manual_operation_mode`** — while in `manual`, cycles the sub-mode above (`normal / bow / crab`) via joystick buttons
Both mode nodes accept changes via joystick buttons, a `String` command topic, or a ROS parameter — so mode can be driven from teleoperation, the dashboard, or a command-line/service call interchangeably.

## Manual Mode Behaviour Analysis

A breakdown of exactly what the vessel does in each manual sub-mode, based on `vessel_control.py`.

### Normal — coupled thrust & steering

| Axis | Drives |
|---|---|
| Throttle | Both left and right thrusters, identical value |
| Steering | Both left and right thruster angles, identical |

Left and right thrusters always move together — same thrust, same angle. This isn't differential (tank-style) steering; it behaves like a single steerable outboard duplicated on both sides, similar to a rudder-and-throttle boat. Bow thruster is forced off.

### Bow — lateral nudge only

| Axis | Drives |
|---|---|
| Throttle | Bow thruster only|

Left and right thrusters are shut off and locked straight ahead. The bow thruster fires port/starboard for close-quarters nudging, with zero forward propulsion. It reuses the same scale (2000) as full forward drive in Normal mode — worth revisiting once real bow thruster limits are known.

### Crab — decoupled heading-hold + lateral strafe

Two independent control loops run simultaneously:

**Heading loop (closed-loop, via external PID):**

| Axis | Effect |
|---|---|
| Twist | Nudges the target heading ±1°/tick |

On entering Crab mode, the current heading is locked in as the initial target. `vessel_control` only sets the target and reports actual heading (`desired_heading` / `current_heading`) — it does not compute the correction itself. The external `heading_pid` node closes the loop and applies its output to the bow thruster independently, at its own update rate (not tied to joystick input).

**Lateral loop (open-loop, direct from joystick):**

| Axis | Drives |
|---|---|
| Joystick | Left/right thrust direction (`atan2`) and magnitude, identical on both sides |

Left and right thrusters point in the strafe direction and fire together — omnidirectional lateral movement rather than fore/aft drive. Combined with the heading loop, this lets the vessel move sideways or diagonally while holding (or slowly adjusting) a fixed heading — true crab-walking.

### Idle / Emergency — hard stop

All five outputs (`left_thrust`, `right_thrust`, `bow_thrust`, `left_pos`, `right_pos`) are forced to `0.0` every cycle, unconditionally, regardless of joystick input.

### Summary

| Mode | Left/Right thrusters | Bow thruster | Forward motion | Lateral motion | Heading control |
|---|---|---|---|---|---|
| **Normal** | Coupled thrust + steering | Off | ✅ | ❌ | Manual (via steering) |
| **Bow** | Off | Manual throttle | ❌ | Nudge only | Manual (via bow nudge) |
| **Crab** | Strafe thrust + direction | PID-controlled | ❌ | ✅ | Automatic (PID hold) |
| **Idle / Emergency** | Off | Off | ❌ | ❌ | — |
---
 
## Remote Teleoperation
 
The vessel — simulated or physical — is driven the same way: joystick input published on `/xros/joy` flows into `mode_selector` and `manual_operation_mode` for state control, and into `vessel_control` for direct thrust/steering commands.
 
```text
Joystick ──► joy_node ──► /xros/joy ──┬──► mode_selector
                                      ├──► manual_operation_mode
                                      └──► vessel_control ──► Thrusters
```
 
```bash
ros2 launch launch_files xros_bringup.launch.py
```
 
This single launch file brings up the full stack — joystick input, mode management, vessel control, heading-hold PID, and the waypoint/POI mission services — against either the VRX simulation or the physical vessel, depending on which thruster topics are active.

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

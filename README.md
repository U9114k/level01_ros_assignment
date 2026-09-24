# Level 1: ROS2 Navigation Assignment - Urvi Kulkarni

## Overview

This assignment implements a modular ROS2 navigation workflow for the ERIC Robotics Testbed-T1.0.0 using ROS2 Humble, Gazebo Classic 11.10.2, RViz2, and the Nav2 navigation stack.

Instead of using `nav2_bringup`, the navigation system was manually configured using the individual Nav2 components and plugins. The implementation separates map loading, localization, planning, control, behavior execution, and lifecycle management into independent components.

The completed system consists of:

- A dedicated `testbed_navigation` ROS2 package.
- Manual map loading using the Nav2 `map_server` plugin.
- AMCL-based localization.
- NavFn global planning.
- DWB local trajectory control.
- Global and local costmaps.
- BT Navigator for navigation execution.
- Nav2 behavior plugins.
- Lifecycle management for the navigation components.
- Separate launch files for map loading, localization, and navigation.
- A master launch file for starting the complete navigation system.

The final navigation workflow is:

```text
Gazebo Testbed
      │
      ├── /odom
      └── /scan
           │
           ▼
     Map Server + AMCL
           │
           ▼
      Robot Localization
           │
           ▼
     Navigation Goal
        from RViz
           │
           ▼
      BT Navigator
       ┌────┴────┐
       ▼         ▼
    NavFn       DWB
   Planner   Controller
       │         │
       └────┬────┘
            ▼
         /cmd_vel
            │
            ▼
      Robot in Gazebo
```

---

## Repository Structure

The completed repository contains the original testbed packages and the newly developed navigation package:

```text
level01_ros_assignment/
├── testbed_description/
├── testbed_gazebo/
├── testbed_bringup/
├── testbed_navigation/
├── BUGS.txt
├── help.md
└── README.md
```

The `testbed_navigation` package is structured as:

```text
testbed_navigation/
├── CMakeLists.txt
├── package.xml
├── README.md
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
└── launch/
    ├── map_loader.launch.py
    ├── localization.launch.py
    ├── navigation.launch.py
    └── navigation_system.launch.py
```

The provided map is located at:

```text
testbed_bringup/maps/
├── testbed_world.yaml
└── testbed_world.pgm
```

---

## Assignment Approach

The navigation stack was implemented incrementally rather than relying on `nav2_bringup`.

The implementation was divided into three independently launchable stages:

1. Map loading
2. Localization
3. Navigation

A fourth master launch file combines these components with the existing testbed simulation so that the complete system can be started with a single command.

This approach preserves the modular structure requested in the assignment while making the complete system easier to run and test.

---

## 1. Map Loading

### `map_loader.launch.py`

The map loading stage uses the Nav2 `map_server` plugin.

The provided map is:

```text
testbed_bringup/maps/testbed_world.yaml
```

The launch file starts:

- `nav2_map_server/map_server`
- `nav2_lifecycle_manager/lifecycle_manager`

The map server loads the occupancy-grid YAML file and publishes the map in the `map` frame.

Simulation time is enabled because the navigation system runs inside Gazebo.

### Launch

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

The map was verified in RViz before proceeding with localization and navigation.

---

## 2. Localization

### `localization.launch.py`

Localization is implemented using the Nav2 AMCL plugin.

The AMCL parameters are stored in:

```text
testbed_navigation/config/amcl_params.yaml
```

The localization launch file starts:

- `nav2_amcl/amcl`
- `nav2_lifecycle_manager/lifecycle_manager`

The main navigation frames are:

```text
map
 └── odom
      └── base_footprint
           └── base_link
                └── lidar_link_1
```

AMCL uses the simulated LiDAR and odometry:

```text
/scan
/odom
```

The main AMCL frame configuration is:

```text
global_frame_id: map
odom_frame_id: odom
base_frame_id: base_footprint
scan_topic: /scan
```

### Launch

```bash
ros2 launch testbed_navigation localization.launch.py
```

---

## 3. Initial Pose in RViz

After the map and AMCL are running, the robot's approximate initial pose is provided through RViz using the **2D Pose Estimate** tool.

The procedure is:

1. Display the map in RViz.
2. Set the RViz fixed frame to `map`.
3. Select **2D Pose Estimate**.
4. Click approximately at the robot's current position on the map.
5. Drag the arrow to indicate the robot's approximate orientation.
6. AMCL uses this as the initial pose.
7. AMCL then refines the robot pose using LiDAR observations and odometry.

The initial pose is therefore used to initialize AMCL; it does not directly command the robot.

Once localization is established, a navigation goal can be sent through RViz.

---

## 4. Navigation

### `navigation.launch.py`

The navigation stage is manually configured using individual Nav2 servers rather than `nav2_bringup`.

The following components are launched:

- Planner Server
- Controller Server
- BT Navigator
- Behavior Server
- Navigation Lifecycle Manager

The navigation parameters are stored in:

```text
testbed_navigation/config/nav2_params.yaml
```

The main plugins are:

| Component | Plugin |
|---|---|
| Global Planner | `nav2_navfn_planner/NavfnPlanner` |
| Local Controller | `dwb_core::DWBLocalPlanner` |
| Global Costmap | Static Layer + Obstacle Layer + Inflation Layer |
| Local Costmap | Obstacle Layer + Inflation Layer |
| BT Navigator | Nav2 Behavior Tree plugins |
| Behavior Server | Spin + BackUp + DriveOnHeading + Wait |

### Launch

```bash
ros2 launch testbed_navigation navigation.launch.py
```

---

## 5. Global Planner

The global planner uses:

```text
nav2_navfn_planner/NavfnPlanner
```

NavFn generates a global path from the robot's current localized position to the requested navigation goal using the global costmap.

The global planner operates in the `map` frame and uses the static map together with the obstacle and inflation information provided by the global costmap.

---

## 6. Local Controller

The local controller uses:

```text
dwb_core::DWBLocalPlanner
```

DWB evaluates candidate local trajectories and selects a suitable trajectory for following the global path while considering the local costmap and nearby obstacles.

Velocity commands are published through:

```text
/cmd_vel
```

These commands are consumed by the simulated robot controller in Gazebo.

The configured DWB critics include:

- RotateToGoal
- Oscillation
- BaseObstacle
- GoalAlign
- PathAlign
- PathDist
- GoalDist

---

## 7. Costmaps

Two costmaps are configured for the navigation system.

### Global Costmap

The global costmap operates in the `map` frame and uses:

- Static Layer
- Obstacle Layer
- Inflation Layer

The static layer receives the occupancy-grid map.

The obstacle layer uses the simulated LiDAR:

```text
/scan
```

The inflation layer provides a safety buffer around obstacles.

### Local Costmap

The local costmap operates in the `odom` frame using a rolling window around the robot.

It uses:

- Obstacle Layer
- Inflation Layer

The local costmap allows the DWB controller to react to nearby obstacles while following the global path.

---

## 8. Behavior Tree Navigator

The BT Navigator coordinates the navigation workflow.

A navigation request follows the general sequence:

```text
Navigation Goal
      │
      ▼
 BT Navigator
      │
      ├── Compute Path
      │       │
      │       ▼
      │   NavFn Planner
      │
      ├── Follow Path
      │       │
      │       ▼
      │   DWB Controller
      │
      └── Recovery / Behaviors
```

The configured Behavior Tree plugins support actions including:

- Compute Path to Pose
- Follow Path
- Spin
- Back Up
- Wait
- Clear Costmap
- Goal checking
- Recovery behavior execution

---

## 9. Behavior Server

The behavior server provides the following behaviors:

```text
Spin
BackUp
DriveOnHeading
Wait
```

These behaviors are configured in `nav2_params.yaml` and managed by the navigation lifecycle manager.

---

## 10. Lifecycle Management

Lifecycle managers are used for the different stages of the navigation system.

The map loading stage manages the map server.

The localization stage manages AMCL.

The navigation stage manages:

- Planner Server
- Controller Server
- BT Navigator
- Behavior Server

This ensures that the required Nav2 components transition through their lifecycle states and become active before navigation is performed.

---

## 11. Launch Files

### Map Loading

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

Starts the map server and its lifecycle manager.

### Localization

```bash
ros2 launch testbed_navigation localization.launch.py
```

Starts AMCL and its lifecycle manager.

### Navigation

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Starts the manually configured Nav2 navigation components.

### Complete Navigation System

A master launch file is also provided:

```bash
ros2 launch testbed_navigation navigation_system.launch.py
```

The master launch file combines:

- The existing Testbed Gazebo/RViz bringup
- Map loading
- AMCL localization
- Nav2 navigation

This allows the complete system to be started using a single command while retaining the separate launch files required by the assignment.

After the system starts, the operator workflow is:

```text
2D Pose Estimate
       │
       ▼
   Localization
       │
       ▼
 Navigation Goal
       │
       ▼
   Nav2 Planning
       │
       ▼
 Robot Navigation
```

---

## 12. Navigation Testing

The complete navigation workflow was tested in the provided Gazebo environment.

### Step 1 – Start the system

The complete system can be started using:

```bash
ros2 launch testbed_navigation navigation_system.launch.py
```

The individual launch files can also be used independently when testing specific components.

### Step 2 – Verify the map

The occupancy-grid map is displayed in RViz.

### Step 3 – Set the initial pose

The **2D Pose Estimate** tool is used to provide AMCL with the approximate initial robot pose.

### Step 4 – Verify localization

The robot pose and TF relationships are checked in RViz.

### Step 5 – Send a navigation goal

A navigation goal is selected in RViz using the navigation goal tool.

The goal specifies:

- Target position
- Target orientation

### Step 6 – Observe navigation

Nav2 computes a global path using NavFn and the DWB controller follows the path using `/cmd_vel`.

The robot's movement is observed in Gazebo while RViz provides the navigation visualization.

---

## 13. Testing and Verification

The following components were verified during testing:

- Gazebo simulation
- RViz2 visualization
- Map server
- Static map
- AMCL
- `/scan` LiDAR data
- `/odom` odometry
- TF transformations
- Global costmap
- Local costmap
- NavFn planner
- DWB controller
- BT Navigator
- Behavior Server
- Lifecycle Manager
- RViz navigation goals

The Nav2 servers successfully transitioned to their active lifecycle states.

Navigation goals were sent from RViz and the robot was observed moving in Gazebo in response to the requested goals.

A short video was recorded showing the localization and navigation workflow in RViz together with the corresponding robot movement in Gazebo.

---

## 14. Challenges and Bugs Identified

The starter repository contained several issues that had to be identified and corrected before the navigation system could be integrated.

A separate `BUGS.txt` file is included in the repository root as requested by the assignment.

### 14.1 Incorrect Map Filename

The supplied map YAML referenced an incorrect/non-existent PGM file.

The map reference was corrected to:

```text
testbed_world.pgm
```

### 14.2 Map Files Not Installed

The `testbed_bringup` CMake configuration did not install the `maps` directory.

The CMake install rules were updated so that the map files are available from the installed package.

### 14.3 Gazebo Models Not Installed

The `testbed_gazebo` CMake configuration did not install the `models` directory.

The CMake install rules were updated to include the Gazebo models.

### 14.4 Malformed Gazebo XML

A malformed XML tag was found in:

```text
testbed_description/urdf/testbed.gazebo
```

An extra `>` character was removed from the affected tag.

### 14.5 Incorrect `ament_package()` Invocation

The description package contained an incorrect invocation of:

```cmake
ament_package
```

It was corrected to:

```cmake
ament_package()
```

### 14.6 Manual Nav2 Integration

The main implementation challenge was configuring Nav2 without relying on `nav2_bringup`.

Each required navigation component had to be configured explicitly, including:

- Planner Server
- Controller Server
- Global Costmap
- Local Costmap
- BT Navigator
- Behavior Server
- Lifecycle Manager
- Planner plugin
- Controller plugin
- Behavior Tree plugins

During integration, the configuration was adjusted to ensure that the planner, controller, costmaps, BT Navigator, behavior server, and lifecycle manager operated together correctly.

---

## 15. Build Instructions

From the workspace root:

```bash
cd ~/assignment_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

The navigation package can also be rebuilt independently:

```bash
colcon build --packages-select testbed_navigation --symlink-install
source install/setup.bash
```

---

## 16. Final Navigation Pipeline

The final system can be summarized as:

```text
                  Static Map
                      │
                      ▼
                  Map Server
                      │
                      ▼
              ┌────── AMCL ──────┐
              │                  │
              │   Localization   │
              │                  │
              ▼                  │
         Robot Pose              │
              │                  │
              └────────┬─────────┘
                       ▼
                Navigation Goal
                   from RViz
                       │
                       ▼
                 BT Navigator
                       │
              ┌────────┴────────┐
              ▼                 ▼
        NavFn Planner      DWB Controller
              │                 │
              └────────┬────────┘
                       ▼
                    /cmd_vel
                       │
                       ▼
                 Gazebo Robot
```

The implementation demonstrates a complete modular ROS2 navigation pipeline using the individual Nav2 components rather than `nav2_bringup`.

---

## 17. Submission Evidence

The submission includes visual evidence of the completed system.

The evidence demonstrates:

- The simulated robot in Gazebo.
- The navigation map in RViz.
- Robot localization using **2D Pose Estimate**.
- Navigation goals issued through RViz.
- Nav2 planning and control.
- Robot movement in Gazebo while executing navigation.
- Successful activation of the Nav2 navigation stack.

A short video is provided as the primary demonstration of localization and navigation, with screenshots available as supplementary evidence.

---

## Contact Info

- Name: Urvi Kulkarni
- Contact number: +91 7760061440
- Email Address: kulkarniurvi94@gmail.com

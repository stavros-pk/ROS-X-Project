#!/usr/bin/env python3
"""
Publishes a list of GPS waypoints for vessel navigation as a
geographic_msgs/msg/GeoPath message.
 
Waypoints are given directly in code as a simple list of [lat, lon] pairs:
    WAYPOINTS = [[lat1, lon1], [lat2, lon2], ...]

    ros2 service call /vessel/add_waypoint data_interfaces/srv/AddWaypoint "{latitude: 37.99, longitude: 23.74}"
    ros2 service call /vessel/get_route data_interfaces/srv/GetWaypoints
    ros2 service call /vessel/get_current_waypoint data_interfaces/srv/GetWaypoints  
"""
 
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
from geographic_msgs.msg import GeoPath, GeoPoseStamped
from data_interfaces.srv import GetWaypoints, AddWaypoint


# --- Edit waypoints: [[lat, lon], [lat, lon], ...] ---
WAYPOINTS = [
    [37.9838, 23.7275],
    [37.9850, 23.7300],
    [37.9870, 23.7330],
    [37.9890, 23.7360],
]
 
FRAME_ID = 'wgs84'
PUBLISH_RATE_HZ = 1.0


class WaypointServiceNode(Node):
 
    def __init__(self):
        super().__init__('waypoint_service_node')

 
        self.get_current_srv = self.create_service(GetWaypoints, 'vessel/get_current_waypoint', self.handle_get_current_waypoint)
        self.add_srv = self.create_service(AddWaypoint, 'vessel/add_waypoint', self.handle_add_waypoint)
        self.get_route = self.create_service(GetWaypoints, '/vessel/get_route', self.handle_get_route)

        self.waypoints = list(WAYPOINTS)
        self.current_index = 0

        self.get_logger().info(
            f'Loaded {len(WAYPOINTS)} waypoints. '
            f'Currently at index {self.current_index}.'
        )
 
    def _make_pose(self, lat, lon):
        pose = GeoPoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = FRAME_ID
        pose.pose.position.latitude = lat
        pose.pose.position.longitude = lon
        pose.pose.position.altitude = 0.0
        pose.pose.orientation.w = 1.0
        return pose
 
    def handle_get_current_waypoint(self, request, response):
        if 0 <= self.current_index < len(WAYPOINTS):
            self.current_index = request.waypoint_index
            lat, lon = WAYPOINTS[self.current_index]
            response.waypoint = self._make_pose(lat, lon)
            response.valid = True
            self.get_logger().info(
                f'Served current waypoint #{self.current_index}: lat={lat}, lon={lon}'
            )
        else:
            response.waypoint = GeoPoseStamped()
            response.valid = False
            self.get_logger().warn('No current waypoint - list exhausted')
 
        return response

    def handle_add_waypoint(self, request, response):
        self.waypoints.append([request.latitude, request.longitude])
        response.success = True
        response.total_waypoints = len(self.waypoints)
        self.get_logger().info(
            f'Added waypoint lat={request.latitude}, lon={request.longitude} '
            f'(total now {len(self.waypoints)})'
        )
        return response
    
    def handle_get_route(self, request, response):
        path = GeoPath()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = FRAME_ID

        for lat, lon in self.waypoints:
            path.poses.append(self._make_pose(lat, lon))

        response.path = path
        self.get_logger().info(f'Served full route: {len(path.poses)} waypoints')
        return response

# =========================================================================
# Entry point
# =========================================================================

def main(args=None):
    rclpy.init(args=args)
    node = WaypointServiceNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
 
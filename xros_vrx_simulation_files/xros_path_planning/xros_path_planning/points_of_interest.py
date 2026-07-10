#!/usr/bin/env python3
"""
Serves Points of Interest (POIs) for vessel navigation - separate from
the waypoint route. A POI is any marked location (hazard, dock, buoy,
fishing ground, etc.) that isn't necessarily part of the vessel's path.

Services:
- 'vessel/add_poi'    -> add a new POI (name, category, lat, lon)
- 'vessel/get_pois'   -> return the full list of POIs
- 'vessel/remove_poi' -> remove a POI by name

ros2 service call /vessel/add_poi data_interfaces/srv/AddPoi "{name: 'Fuel Dock', category: 'dock', latitude: 37.9838, longitude: 23.7275}"
ros2 service call /vessel/get_pois data_interfaces/srv/GetPois
ros2 service call /vessel/remove_poi data_interfaces/srv/RemovePoi "{name: 'Fuel Dock'}"
"""

import rclpy
from rclpy.node import Node
from data_interfaces.msg import Poi
from data_interfaces.srv import AddPoi, GetPois, RemovePoi


class POIServiceNode(Node):

    def __init__(self):
        super().__init__('poi_service_node')
        self.pois = []  # list of POI msg instances

        self.add_srv = self.create_service(
            AddPoi, 'vessel/add_poi', self.handle_add_poi
        )
        self.get_srv = self.create_service(
            GetPois, 'vessel/get_pois', self.handle_get_pois
        )
        self.remove_srv = self.create_service(
            RemovePoi, 'vessel/remove_poi', self.handle_remove_poi
        )

        self.get_logger().info('POI service node ready (0 POIs loaded).')

    def handle_add_poi(self, request, response):
        poi = Poi()
        poi.name = request.name
        poi.category = request.category
        poi.latitude = request.latitude
        poi.longitude = request.longitude

        self.pois.append(poi)

        response.success = True
        response.total_pois = len(self.pois)
        self.get_logger().info(
            f'Added POI "{poi.name}" ({poi.category or "uncategorized"}) '
            f'at lat={poi.latitude}, lon={poi.longitude} '
            f'(total now {len(self.pois)})'
        )
        return response

    def handle_get_pois(self, request, response):
        response.pois = self.pois
        self.get_logger().info(f'Served {len(self.pois)} POIs')
        return response

    def handle_remove_poi(self, request, response):
        before = len(self.pois)
        self.pois = [p for p in self.pois if p.name != request.name]
        removed = before - len(self.pois)

        if removed > 0:
            response.success = True
            self.get_logger().info(f'Removed POI "{request.name}"')
        else:
            response.success = False
            self.get_logger().warn(f'No POI named "{request.name}" found')

        response.total_pois = len(self.pois)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = POIServiceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
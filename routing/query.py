import common
import json
from routing import core as routing_core


class Query:
    def __init__(self, gtfs_file_name, road_data_file_name):
        print(f"Loading consolidated transit data from '{gtfs_file_name}'")
        with open(gtfs_file_name, "r", encoding="utf-8") as file:
            self.transit_map = json.loads(file.read())

        print(f"Loading processed road adjacency data from '{road_data_file_name}'\n")
        with open(road_data_file_name, "r", encoding="utf-8") as file:
            self.road_map = json.loads(file.read())

        # build KD trees
        self.bus_tree, self.bus_nodes = routing_core.build_kd_tree(self.transit_map["bus_stops"])
        self.luas_tree, self.luas_nodes = routing_core.build_kd_tree(self.transit_map["luas_stops"])
        self.dart_tree, self.dart_nodes = routing_core.build_kd_tree(self.transit_map["dart_stops"])
        self.road_tree, self.road_nodes = routing_core.build_kd_tree(self.road_map)

    def transit_walking_route(self, start, end, mode):
        print(f"[Computing {mode}-walking routes from {start} to {end}] Straightline distance: {routing_core.haversine_distance(*start, *end)}\n")
        road_node_start = routing_core.get_nearest_nodes(start, self.road_tree, self.road_nodes, 2)[0]
        road_node_end = routing_core.get_nearest_nodes(end, self.road_tree, self.road_nodes, 2)[0]

        # different k values for different transports
        k = common.k_nearest_mappings[mode]

        tree_ref = eval(f"self.{mode}_tree")
        nodes_ref = eval(f"self.{mode}_nodes")

        nearest_stops_start = routing_core.get_nearest_nodes(start, tree_ref, nodes_ref, k)
        nearest_stops_end = routing_core.get_nearest_nodes(end, tree_ref, nodes_ref, k)

        transit_routes = routing_core.get_transit_routes(nearest_stops_start, nearest_stops_end,
                                                         self.transit_map, mode)
        ans_route, ans_walking_time, ans_transit_time, ans_total_time = None, 99999, 99999, 99999
        ans_walking_route_start, ans_walking_route_end = None, None

        for transit_route in transit_routes:
            start_stop, end_stop, route_label, distance, trace, start_wait_time = transit_route

            transit_time = (distance / common.average_speeds[mode]) * 60

            # get walking route to the start stop
            road_node_start_stop = routing_core.get_nearest_nodes(
                (
                    self.transit_map[f"{mode}_stops"][start_stop]["lat"],
                    self.transit_map[f"{mode}_stops"][start_stop]["lon"]
                ), self.road_tree, self.road_nodes, 2
            )[0]

            walking_route_start = routing_core.get_shortest_path_road(road_node_start, road_node_start_stop, self.road_map)
            walking_distance_start = routing_core.get_route_distance(walking_route_start)
            walking_time_start = (walking_distance_start / common.average_speeds['walking']) * 60

            # get walking route to the end stop
            road_node_end_stop = routing_core.get_nearest_nodes(
                (
                    self.transit_map[f"{mode}_stops"][end_stop]["lat"],
                    self.transit_map[f"{mode}_stops"][end_stop]["lon"]
                ), self.road_tree, self.road_nodes, 2
            )[0]
            walking_route_end = routing_core.get_shortest_path_road(road_node_end, road_node_end_stop, self.road_map)
            walking_distance_end = routing_core.get_route_distance(walking_route_end)
            walking_time_end = (walking_distance_end / common.average_speeds['walking']) * 60

            walking_time = walking_time_start + walking_time_end

            delta_wait_walking = walking_time - start_wait_time
            if delta_wait_walking < 0:
                delta_wait_walking = 0

            # TODO: currently basic method to check time delta betweeen walking and vehicle arrival
            candidate_time = walking_time + delta_wait_walking
            total_time = walking_time_end + transit_time + walking_time_end

            # print(
            #     f"*Transit route {route_label}: {self.transit_map[f'{mode}_stops'][start_stop]['name']} -> {self.transit_map[f'{mode}_stops'][end_stop]['name']}")
            # print(f"Start walking: {walking_distance_start} KM, {walking_time_start} mins")
            # print(f"Transit: {distance} KM, {transit_time} mins")
            # print(f"End walking: {walking_distance_end} KM, {walking_time_end} mins")
            # print("Total time:", total_time, "mins")
            # print("Total walking time:", walking_time, "mins")
            # print("Total wait time:", start_wait_time, "mins\n")

            if candidate_time < ans_walking_time:
                ans_walking_time = walking_time
                ans_total_time = total_time
                ans_route = transit_route
                ans_transit_time = transit_time
                ans_walking_route_start, ans_walking_route_end = walking_route_start, walking_route_end

        if ans_route:
            print("\n\nAnswer route: ")
            start_stop, end_stop, route_label, distance, trace, wait_time = ans_route
            print(
                f"*Transit route {route_label}: {self.transit_map[f'{mode}_stops'][start_stop]['name']} -> {self.transit_map[f'{mode}_stops'][end_stop]['name']}")
            print("Total time:", ans_total_time, "mins")
            print("Total walking time:", ans_walking_time, "mins")
            print("Total wait time:", wait_time, "mins")

            return {
                "start": start,
                "end": end,
                mode: {
                    "start_stop": (self.transit_map[f'{mode}_stops'][start_stop]['lat'], self.transit_map[f'{mode}_stops'][start_stop]['lon']),
                    "end_stop": (self.transit_map[f'{mode}_stops'][end_stop]['lat'], self.transit_map[f'{mode}_stops'][end_stop]['lon']),
                    "label": route_label,
                    "distance": distance,
                    "trace": trace,
                    "wait_time": wait_time,
                    "transit_time": ans_transit_time,
                },
                "walk_start": ans_walking_route_start,
                "walk_end": ans_walking_route_end,
            }
        else:
            print("No direct route found")
            return None

    def middle_point(self, start, end):
        print(f"[Middle point between {start} and {end}]")
        start_id = routing_core.get_nearest_nodes(start, self.road_tree, self.road_nodes, 2)[0]
        end_id = routing_core.get_nearest_nodes(end, self.road_tree, self.road_nodes, 2)[0]

        route = routing_core.get_shortest_path_road(start_id, end_id, self.road_map)

        return route[len(route)//2]

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

    def get_route_options(self, start, end):
        sols = self.transit_route(start, end)

        print("----", sols.keys(), "----")
        print(len(sols["bus-luas"]))
        print(len(sols["bus-shrink"]))

        # bus and luas combo routes
        # bus - luas - bus
        all_combinations = {"bus-luas": [], "bus-shrink": [], "bus-split": []}
        for sol in sols["bus-luas"]:
            sol_processed = {
                "distance_walk": 0,
                "distance_luas": 0,
                "distance_bus": 0,
                "segments": []
            }
            # no initial bus
            if sol[0]["type"] == "luas":
                # add walking path to luas stop
                sol_processed["segments"].append({
                    "type": "walk",
                    "distance": sol[0]["start_offset"],
                    "path": sol[0]["walking_path_to_start_stop"]
                })
                sol_processed["distance_walk"] += sol[0]["start_offset"]

                # add luas path
                sol_processed["segments"].append({
                    "type": "luas",
                    "distance": sol[0]["distance"],
                    "path": sol[0]["path"],
                    "start_stop": self.transit_map["luas_stops"][sol[0]["start_stop"]]["name"],
                    "start_stop_coordinate": sol[0]["start_stop_coord"],
                    "end_stop": self.transit_map["luas_stops"][sol[0]["end_stop"]]["name"],
                    "end_stop_coordinate": sol[0]["end_stop_coord"],
                    "wait_times": sol[0]["wait_times"],
                    "route": sol[0]["route_label"],
                })
                sol_processed["distance_luas"] += sol[0]["distance"]
            # initial bus
            else:
                # add walking path to bus stop
                sol_processed["segments"].append({
                    "type": "walk",
                    "distance": sol[0]["start_offset"],
                    "path": sol[0]["walking_path_to_start_stop"]
                })
                sol_processed["distance_walk"] += sol[0]["start_offset"]

                # add bus path
                sol_processed["segments"].append({
                    "type": "bus",
                    "distance": sol[0]["distance"],
                    "path": sol[0]["path"],
                    "start_stop": self.transit_map["bus_stops"][sol[0]["start_stop"]]["name"],
                    "start_stop_coordinate": sol[0]["start_stop_coord"],
                    "end_stop": self.transit_map["bus_stops"][sol[0]["end_stop"]]["name"],
                    "end_stop_coordinate": sol[0]["end_stop_coord"],
                    "wait_times": sol[0]["wait_times"],
                    "route": sol[0]["route_label"],
                })
                sol_processed["distance_bus"] += sol[0]["distance"]

                # add walking path to luas stop
                bus_stop_getoff_point = routing_core.get_nearest_nodes(sol[0]["end_stop_coord"], self.road_tree, self.road_nodes, 2)[0]
                luas_stop_hopon_point = routing_core.get_nearest_nodes(sol[1]["start_stop_coord"], self.road_tree, self.road_nodes, 2)[0]
                walk_path = routing_core.get_shortest_path_road(bus_stop_getoff_point, luas_stop_hopon_point, self.road_map)
                walk_distance = routing_core.get_route_distance(walk_path)
                sol_processed["segments"].append({
                    "type": "walk",
                    "distance": walk_distance,
                    "path": walk_path
                })
                sol_processed["distance_walk"] += walk_distance

                # add luas path
                sol_processed["segments"].append({
                    "type": "luas",
                    "distance": sol[1]["distance"],
                    "path": sol[1]["path"],
                    "start_stop": self.transit_map["luas_stops"][sol[1]["start_stop"]]["name"],
                    "start_stop_coordinate": sol[1]["start_stop_coord"],
                    "end_stop": self.transit_map["luas_stops"][sol[1]["end_stop"]]["name"],
                    "end_stop_coordinate": sol[1]["end_stop_coord"],
                    "wait_times": sol[1]["wait_times"],
                    "route": sol[1]["route_label"],
                })
                sol_processed["distance_luas"] += sol[1]["distance"]

            # no final bus
            if sol[-1]["type"] == "luas":
                # add walking path from luas stop
                sol_processed["segments"].append({
                    "type": "walk",
                    "distance": sol[-1]["end_offset"],
                    "path": sol[-1]["walking_path_from_end_stop"]
                })
                sol_processed["distance_walk"] += sol[-1]["end_offset"]
            # final bus
            else:
                # add walking path from luas stop to bus stop
                sol_processed["segments"].append({
                    "type": "walk",
                    "distance": sol[-1]["start_offset"],
                    "path": sol[-1]["walking_path_to_start_stop"]
                })
                sol_processed["distance_walk"] += sol[-1]["start_offset"]

                # add bus path
                sol_processed["segments"].append({
                    "type": "bus",
                    "distance": sol[-1]["distance"],
                    "path": sol[-1]["path"],
                    "start_stop": self.transit_map["bus_stops"][sol[-1]["start_stop"]]["name"],
                    "start_stop_coordinate": sol[-1]["start_stop_coord"],
                    "end_stop": self.transit_map["bus_stops"][sol[-1]["end_stop"]]["name"],
                    "end_stop_coordinate": sol[-1]["end_stop_coord"],
                    "wait_times": sol[-1]["wait_times"],
                    "route": sol[-1]["route_label"],
                })
                sol_processed["distance_bus"] += sol[-1]["distance"]

                # add walking path from bus stop
                sol_processed["segments"].append({
                    "type": "walk",
                    "distance": sol[-1]["end_offset"],
                    "path": sol[-1]["walking_path_from_end_stop"]
                })
                sol_processed["distance_walk"] += sol[-1]["end_offset"]

            all_combinations["bus-luas"].append(sol_processed)

        for sol in sols["bus-shrink"]:
            sol_processed = {
                "distance_walk": 0,
                "distance_luas": 0,
                "distance_bus": 0,
                "segments": []
            }

            # add walking path to bus stop
            sol_processed["segments"].append({
                "type": "walk",
                "distance": sol[0]["start_offset"],
                "path": sol[0]["walking_path_to_start_stop"]
            })
            sol_processed["distance_walk"] += sol[0]["start_offset"]

            # add bus path
            sol_processed["segments"].append({
                "type": "bus",
                "distance": sol[0]["distance"],
                "path": sol[0]["path"],
                "start_stop": self.transit_map["bus_stops"][sol[0]["start_stop"]]["name"],
                "start_stop_coordinate": sol[0]["start_stop_coord"],
                "end_stop": self.transit_map["bus_stops"][sol[0]["end_stop"]]["name"],
                "end_stop_coordinate": sol[0]["end_stop_coord"],
                "wait_times": sol[0]["wait_times"],
                "route": sol[0]["route_label"],
            })
            sol_processed["distance_bus"] += sol[0]["distance"]

            # add walking path from bus stop
            sol_processed["segments"].append({
                "type": "walk",
                "distance": sol[0]["end_offset"],
                "path": sol[0]["walking_path_from_end_stop"]
            })
            sol_processed["distance_walk"] += sol[0]["end_offset"]

            all_combinations["bus-shrink"].append(sol_processed)

        for sol in sols["bus-split"]:
            sol_processed = {
                "distance_walk": 0,
                "distance_luas": 0,
                "distance_bus": 0,
                "segments": []
            }

            # add walking path to bus stop
            sol_processed["segments"].append({
                "type": "walk",
                "distance": sol[0]["start_offset"],
                "path": sol[0]["walking_path_to_start_stop"]
            })
            sol_processed["distance_walk"] += sol[0]["start_offset"]

            # add bus path
            sol_processed["segments"].append({
                "type": "bus",
                "distance": sol[0]["distance"],
                "path": sol[0]["path"],
                "start_stop": self.transit_map["bus_stops"][sol[0]["start_stop"]]["name"],
                "start_stop_coordinate": sol[0]["start_stop_coord"],
                "end_stop": self.transit_map["bus_stops"][sol[0]["end_stop"]]["name"],
                "end_stop_coordinate": sol[0]["end_stop_coord"],
                "wait_times": sol[0]["wait_times"],
                "route": sol[0]["route_label"],
            })
            sol_processed["distance_bus"] += sol[0]["distance"]

            # add walking path to luas stop
            bus_stop_getoff_point = routing_core.get_nearest_nodes(sol[0]["end_stop_coord"], self.road_tree, self.road_nodes, 2)[0]
            bus_stop_hopon_point = routing_core.get_nearest_nodes(sol[1]["start_stop_coord"], self.road_tree, self.road_nodes, 2)[0]
            walk_path = routing_core.get_shortest_path_road(bus_stop_getoff_point, bus_stop_hopon_point, self.road_map)
            walk_distance = routing_core.get_route_distance(walk_path)
            sol_processed["segments"].append({
                "type": "walk",
                "distance": walk_distance,
                "path": walk_path
            })
            sol_processed["distance_walk"] += walk_distance

            # add bus path
            sol_processed["segments"].append({
                "type": "bus",
                "distance": sol[1]["distance"],
                "path": sol[1]["path"],
                "start_stop": self.transit_map["bus_stops"][sol[1]["start_stop"]]["name"],
                "start_stop_coordinate": sol[1]["start_stop_coord"],
                "end_stop": self.transit_map["bus_stops"][sol[1]["end_stop"]]["name"],
                "end_stop_coordinate": sol[1]["end_stop_coord"],
                "wait_times": sol[1]["wait_times"],
                "route": sol[1]["route_label"],
            })
            sol_processed["distance_bus"] += sol[1]["distance"]

            # add walking path from bus stop
            sol_processed["segments"].append({
                "type": "walk",
                "distance": sol[1]["end_offset"],
                "path": sol[1]["walking_path_from_end_stop"]
            })
            sol_processed["distance_walk"] += sol[1]["end_offset"]

            all_combinations["bus-split"].append(sol_processed)

        return all_combinations

    def transit_route(self, start, end):
        # 1. compute overall distance - a-star and straightline
        road_node_start_id = routing_core.get_nearest_nodes(start, self.road_tree, self.road_nodes, 2)[0]
        road_node_end_id = routing_core.get_nearest_nodes(end, self.road_tree, self.road_nodes, 2)[0]

        print(f"[Compute transit route from {start} to {end}]")
        print(f"  Straightline distance: {routing_core.haversine_distance(*start, *end)}")

        direct_road_distance = routing_core.get_route_distance(
            routing_core.get_shortest_path_road(road_node_start_id, road_node_end_id, self.road_map))
        print(f"  A-star distance:", direct_road_distance)

        # 2. Select mode based on distance
        # look for direct luas as a bridge

        luas_sols = []
        print("------------------------------------ LUAS ------------------------------------")
        luas_routes = self.transit_route_individual(start, end, road_node_start_id, road_node_end_id, "luas")
        if luas_routes:
            for luas_route in luas_routes:
                luas_sol = []
                print(f"    Label: {luas_route['route_label']}\n    Route length: {luas_route['distance']}\n    Wait time: "
                      f"{luas_route['wait_times']}\n    Start offset: {luas_route['start_offset']}"
                      f"\n    End offset: {luas_route['end_offset']}\n")

                luas_node_start_id = routing_core.get_nearest_nodes(luas_route["start_stop_coord"], self.road_tree, self.road_nodes, 2)[0]
                luas_node_stop_id = routing_core.get_nearest_nodes(luas_route["end_stop_coord"], self.road_tree, self.road_nodes, 2)[0]

                bus_routes_to_start = self.transit_route_individual(start, luas_route["start_stop_coord"], road_node_start_id, luas_node_start_id, "bus")
                bus_routes_to_start_ = []
                if bus_routes_to_start:
                    for bus_route in bus_routes_to_start:
                        if bus_route["start_offset"] + bus_route["end_offset"] < luas_route["start_offset"] - 0.5:
                            print(
                                f"        Label: {bus_route['route_label']}\n        Route length: {bus_route['distance']}\n        Wait time: "
                                f"{bus_route['wait_times']}\n        Start offset: {bus_route['start_offset']}"
                                f"\n        End offset: {bus_route['end_offset']}\n")
                            bus_routes_to_start_.append(bus_route)
                if bus_routes_to_start_:
                    luas_sol.append(bus_routes_to_start_[0])
                luas_sol.append(luas_route)

                bus_routes_to_end = self.transit_route_individual(luas_route["end_stop_coord"], end, luas_node_stop_id, road_node_end_id,
                                                                    "bus")
                bus_routes_to_end_ = []
                if bus_routes_to_end:
                    for bus_route in bus_routes_to_end:
                        if bus_route["start_offset"] + bus_route["end_offset"] < luas_route["end_offset"] - 0.5:
                            print(
                                f"        Label: {bus_route['route_label']}\n        Route length: {bus_route['distance']}\n        Wait time: "
                                f"{bus_route['wait_times']}\n        Start offset: {bus_route['start_offset']}"
                                f"\n        End offset: {bus_route['end_offset']}\n")
                            bus_routes_to_end_.append(bus_route)
                if bus_routes_to_end_:
                    luas_sol.append(bus_routes_to_end_[0])
                luas_sols.append(luas_sol)

        print("-------------------------------------------------------------------------------")

        bus_sols, bus_routes, bus_k = [], None, common.k_nearest_mappings["bus"]
        while not bus_routes:
            print("------- BUS SHRINK -------")
            bus_routes = self.transit_route_individual(start, end, road_node_start_id, road_node_end_id, "bus", bus_k)
            if bus_routes:
                for bus_route in bus_routes:
                    if bus_route["distance"] < 1.1 * direct_road_distance:
                        print(f"    Label: {bus_route['route_label']}\n    Route length: {bus_route['distance']}\n    Wait time: "
                              f"{bus_route['wait_times']}\n    Start offset: {bus_route['start_offset']}"
                              f"\n    End offset: {bus_route['end_offset']}\n")
                        bus_sols.append([bus_route])
            else:
                bus_k += 10
            print("------------------")

        bus_sols = sorted(bus_sols, key=lambda sol: sol[0]["total_distance"])

        # compute bus half split routes

        mid = self.middle_point(start, end)
        road_node_mid_id = routing_core.get_nearest_nodes(mid, self.road_tree, self.road_nodes, 2)[0]

        bus_split_sols, first_halves, bus_fh_k = [], None, common.k_nearest_mappings["bus"]

        while not first_halves:
            print("------- BUS SPLIT FH -------")
            first_halves = self.transit_route_individual(start, mid, road_node_start_id, road_node_mid_id, "bus", bus_fh_k)
            if first_halves:
                print("First halves original (will considered best 5):", len(first_halves))
                first_halves = sorted(first_halves, key=lambda sol: sol["total_distance"])[:5]

                for fh_bus_route in first_halves:
                    get_off_point = fh_bus_route["end_stop_coord"]
                    road_get_off_point_id = routing_core.get_nearest_nodes(get_off_point, self.road_tree, self.road_nodes, 2)[0]

                    second_halves, bus_sh_k = [], common.k_nearest_mappings["bus"]
                    while not second_halves:
                        print("------- BUS SPLIT SH -------")
                        second_halves = self.transit_route_individual(get_off_point, end, road_get_off_point_id, road_node_end_id,
                                                                    "bus", bus_sh_k)
                        if second_halves:
                            print("Second halves original (will consider best 5):", len(second_halves))
                            second_halves = sorted(second_halves, key=lambda sol: sol["total_distance"])[:5]

                            for sh_sh_route in second_halves:
                                bus_split_sols.append([fh_bus_route, sh_sh_route])
                        else:
                            bus_sh_k += 10
                        print("------------------")

            else:
                bus_fh_k += 10
            print("------------------")

        bus_split_sols = sorted(bus_split_sols, key=lambda combination: combination[0]["total_distance"] + combination[1]["total_distance"])

        return {"bus-luas": luas_sols, "bus-shrink": bus_sols[:3], "bus-split": bus_split_sols[:3]}

    def transit_route_individual(self, start, end, road_node_start_id, road_node_end_id, mode, k=None):
        print(f"  *Transit route with mode {mode}*")
        # 1. get k value for the transport mode
        if not k:
            k = common.k_nearest_mappings[mode]

        tree_ref = eval(f"self.{mode}_tree")
        nodes_ref = eval(f"self.{mode}_nodes")

        # 2. get list of nearest transit stops to start and stop points
        nearest_stops_start = routing_core.get_nearest_nodes(start, tree_ref, nodes_ref, k)
        nearest_stops_end = routing_core.get_nearest_nodes(end, tree_ref, nodes_ref, k)

        # 3. Get relevant routes of given transit mode based on time and start/stop points
        transit_routes = routing_core.get_transit_routes(nearest_stops_start, nearest_stops_end,
                                                         self.transit_map, mode)
        print(f"  Found {len(transit_routes)} routes")

        # 4 convert into return format
        return_format = []
        for transit_route in transit_routes:
            start_stop, end_stop, route_label, distance, trace, wait_times = transit_route
            road_node_start_stop = routing_core.get_nearest_nodes(
                (
                    self.transit_map[f"{mode}_stops"][start_stop]["lat"],
                    self.transit_map[f"{mode}_stops"][start_stop]["lon"]
                ), self.road_tree, self.road_nodes, 2
            )[0]
            route_start_offset_path = routing_core.get_shortest_path_road(road_node_start_id, road_node_start_stop,
                                                                      self.road_map)
            route_start_offset_distance = routing_core.get_route_distance(route_start_offset_path)

            road_node_end_stop = routing_core.get_nearest_nodes(
                (
                    self.transit_map[f"{mode}_stops"][end_stop]["lat"],
                    self.transit_map[f"{mode}_stops"][end_stop]["lon"]
                ), self.road_tree, self.road_nodes, 2
            )[0]
            route_end_offset_path = routing_core.get_shortest_path_road(road_node_end_id, road_node_end_stop,
                                                                          self.road_map)
            route_end_offset_distance = routing_core.get_route_distance(route_end_offset_path)

            return_format.append(
                {
                    "type": mode,
                    "start_stop": start_stop,
                    "start_stop_coord": (self.transit_map[f"{mode}_stops"][start_stop]["lat"],
                                         self.transit_map[f"{mode}_stops"][start_stop]["lon"]),
                    "end_stop": end_stop,
                    "end_stop_coord": (self.transit_map[f"{mode}_stops"][end_stop]["lat"],
                                         self.transit_map[f"{mode}_stops"][end_stop]["lon"]),
                    "walking_path_to_start_stop": route_start_offset_path,
                    "walking_path_from_end_stop": route_end_offset_path,
                    "total_distance": distance + route_start_offset_distance + route_end_offset_distance,
                    "distance": distance,
                    "route_label": route_label,
                    "path": trace,
                    "wait_times": wait_times,
                    "start_offset": route_start_offset_distance,
                    "end_offset": route_end_offset_distance,
                }
            )

        return return_format

    def middle_point(self, start, end):
        print(f"[Middle point between {start} and {end}]")
        start_id = routing_core.get_nearest_nodes(start, self.road_tree, self.road_nodes, 2)[0]
        end_id = routing_core.get_nearest_nodes(end, self.road_tree, self.road_nodes, 2)[0]

        route = routing_core.get_shortest_path_road(start_id, end_id, self.road_map)

        return route[len(route) // 2]

import common
from datetime import datetime, timedelta

import heapq
from math import radians, cos, sin, sqrt, atan2
from scipy.spatial import KDTree


def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    # Earth radius in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Difference in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


def build_kd_tree(node_map):
    print("[Build KD Tree for nodes]")
    # Extract node keys and their corresponding lat and lon to build the kd-tree
    nodes = list(node_map.keys())
    coordinates = [(info['lat'], info['lon']) for info in node_map.values()]
    # Construct KDTree with the coordinates
    tree = KDTree(coordinates)
    return tree, nodes


def get_nearest_nodes(root, tree, nodes, k=25):
    # Find the k nearest points (nodes) to the root. The KDTree returns a tuple (distances, indices)
    _, indices = tree.query((root[0], root[1]), k=k)
    # Retrieve the node keys using the indices
    nearest_node_keys = [nodes[i] for i in indices]
    return nearest_node_keys


def get_shortest_path_road(start_id, goal_id, road_map):
    open_set = [(0, start_id, None)]
    came_from = {}

    g_score = {node: float('inf') for node in road_map}
    g_score[start_id] = 0

    f_score = {node: float('inf') for node in road_map}
    f_score[start_id] = haversine_distance(road_map[start_id]['lat'], road_map[start_id]['lon'],
                                           road_map[goal_id]['lat'], road_map[goal_id]['lon'])

    while open_set:
        current_f, current, _ = heapq.heappop(open_set)

        if current == goal_id:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = came_from.get(current)
            return [(road_map[node_id]["lat"], road_map[node_id]["lon"]) for node_id in path[::-1]]

        for neighbor in road_map[current]['neighbors']:
            tentative_g_score = g_score[current] + haversine_distance(road_map[current]['lat'],
                                                                      road_map[current]['lon'],
                                                                      road_map[neighbor]['lat'],
                                                                      road_map[neighbor]['lon'])

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + haversine_distance(road_map[neighbor]['lat'],
                                                                           road_map[neighbor]['lon'],
                                                                           road_map[goal_id]['lat'],
                                                                           road_map[goal_id]['lon'])
                heapq.heappush(open_set, (f_score[neighbor], neighbor, current))

    return None


def parse_time(time_str):
    time_split = time_str.split(":")
    if int(time_split[0]) >= 24:
        time_str = f"{int(time_split[0]) - 24}:{time_split[1]}:{time_split[2]}"
    time_now = datetime.now()
    return datetime.strptime(time_str, "%H:%M:%S").replace(year=time_now.year, month=time_now.month, day=time_now.day)


def get_transit_routes(nearest_stops_start, nearest_stops_end, transit_map, mode="bus"):
    # look for transit combos - this captures transit routes in both directions
    possible_solutions = []
    for start_stop in nearest_stops_start:
        for end_stop in nearest_stops_end:
            start_routes = set(transit_map[f"{mode}_stops"][start_stop]["routes"].keys())
            end_routes = set(transit_map[f"{mode}_stops"][end_stop]["routes"].keys())
            transit_routes = start_routes.intersection(end_routes)
            if transit_routes:
                possible_solutions.append((start_stop, end_stop, transit_routes))

    # filter routes by time possible_solutions at start_stop
    time_now = datetime.now()
    time_weekday = time_now.weekday()
    valid_service_ids = common.service_id_mappings[mode][time_weekday]
    # print("Valid Service IDs: ", valid_service_ids, "\n")

    connected_solutions = []
    for start_stop, end_stop, routes in possible_solutions:
        for route in routes:
            route_0 = route + "_0"
            if route_0 in transit_map[f"{mode}_routes"]:
                i = transit_map[f"{mode}_routes"][route_0].index(start_stop) if start_stop in transit_map[f"{mode}_routes"][route_0] else -1
                j = transit_map[f"{mode}_routes"][route_0].index(end_stop) if end_stop in transit_map[f"{mode}_routes"][route_0] else -1
                distance = 0
                if i != -1 and j != -1 and i < j:
                    prev = transit_map[f"{mode}_routes"][route_0][i]
                    trace = [[transit_map[f"{mode}_stops"][prev]["lat"], transit_map[f"{mode}_stops"][prev]["lon"]]]

                    # computing waiting time
                    service_id_current = None
                    for service_id in valid_service_ids:
                        service_id = str(service_id)
                        # print(service_id, transit_map[f"{mode}_stops"][prev]["routes"][route])
                        if service_id in transit_map[f"{mode}_stops"][prev]["routes"][route]:
                            service_id_current = service_id
                            break
                    if not service_id_current:
                        print(f"  {route_0}: No route found using service id")

                    else:
                        # print(f"  {route_0} service_id_current: {service_id_current}")
                        # lowest_wait_time = timedelta(days=1)
                        # for time_str in transit_map[f"{mode}_stops"][prev]["routes"][route][service_id_current]:
                        #     vehicle_time = parse_time(time_str)
                        #     # If the vehicle time has already passed today, skip it
                        #     if vehicle_time < time_now:
                        #         continue
                        #     wait_time = vehicle_time - time_now
                        #     if wait_time < lowest_wait_time:
                        #         lowest_wait_time = wait_time

                        wait_times = []
                        for time_str in transit_map[f"{mode}_stops"][prev]["routes"][route][service_id_current]:
                            vehicle_time = parse_time(time_str)
                            # If the vehicle time has already passed today, skip it
                            if vehicle_time < time_now:
                                continue
                            wait_time = vehicle_time - time_now
                            # Instead of comparing, just add all future wait times to the list
                            wait_times.append(wait_time.total_seconds() / 60)

                        # Sort the list of wait times
                        wait_times.sort()
                        next_three_wait_times = wait_times[:3] if len(wait_times) >= 3 else wait_times

                        #  only continue if there are actual timelines when bus arrives
                        if next_three_wait_times:
                            # compute rolling distance
                            for transit_stop in transit_map[f"{mode}_routes"][route_0][i + 1:j + 1]:
                                distance += haversine_distance(
                                    transit_map[f"{mode}_stops"][prev]["lat"],
                                    transit_map[f"{mode}_stops"][prev]["lon"],
                                    transit_map[f"{mode}_stops"][transit_stop]["lat"],
                                    transit_map[f"{mode}_stops"][transit_stop]["lon"],
                                )
                                trace.append(
                                    [transit_map[f"{mode}_stops"][transit_stop]["lat"], transit_map[f"{mode}_stops"][transit_stop]["lon"]])
                                prev = transit_stop
                            connected_solutions.append((start_stop, end_stop, route, distance, trace, next_three_wait_times))
                        continue

            route_1 = route + "_1"
            if route_1 in transit_map[f"{mode}_routes"]:
                i = transit_map[f"{mode}_routes"][route_1].index(start_stop) if start_stop in transit_map[f"{mode}_routes"][route_1] else -1
                j = transit_map[f"{mode}_routes"][route_1].index(end_stop) if end_stop in transit_map[f"{mode}_routes"][route_1] else -1
                distance = 0

                if i != -1 and j != -1 and i < j:
                    prev = transit_map[f"{mode}_routes"][route_1][i]
                    trace = [[transit_map[f"{mode}_stops"][prev]["lat"], transit_map[f"{mode}_stops"][prev]["lon"]]]

                    # computing waiting time
                    service_id_current = None
                    for service_id in valid_service_ids:
                        service_id = str(service_id)
                        if service_id in transit_map[f"{mode}_stops"][prev]["routes"][route]:
                            service_id_current = service_id
                            break
                    if not service_id_current:
                        print(f"  {route_1}: No route found using service id")

                    else:
                        # print(f"  {route_0} service_id_current: {service_id_current}")
                        # lowest_wait_time = timedelta(days=1)
                        # for time_str in transit_map[f"{mode}_stops"][prev]["routes"][route][service_id_current]:
                        #     vehicle_time = parse_time(time_str)
                        #     # If the vehicle time has already passed today, skip it
                        #     if vehicle_time < time_now:
                        #         continue
                        #     wait_time = vehicle_time - time_now
                        #     if wait_time < lowest_wait_time:
                        #         lowest_wait_time = wait_time

                        wait_times = []
                        for time_str in transit_map[f"{mode}_stops"][prev]["routes"][route][service_id_current]:
                            vehicle_time = parse_time(time_str)
                            # If the vehicle time has already passed today, skip it
                            if vehicle_time < time_now:
                                continue
                            wait_time = vehicle_time - time_now
                            # Instead of comparing, just add all future wait times to the list
                            wait_times.append(wait_time.total_seconds() / 60)

                        # Sort the list of wait times
                        wait_times.sort()
                        next_three_wait_times = wait_times[:3] if len(wait_times) >= 3 else wait_times

                        # only continue if there are actual timelines when bus arrives
                        if next_three_wait_times:
                            # compute rolling distance
                            for transit_stop in transit_map[f"{mode}_routes"][route_1][i + 1:j + 1]:
                                distance += haversine_distance(
                                    transit_map[f"{mode}_stops"][prev]["lat"],
                                    transit_map[f"{mode}_stops"][prev]["lon"],
                                    transit_map[f"{mode}_stops"][transit_stop]["lat"],
                                    transit_map[f"{mode}_stops"][transit_stop]["lon"],
                                )
                                trace.append(
                                    [transit_map[f"{mode}_stops"][transit_stop]["lat"], transit_map[f"{mode}_stops"][transit_stop]["lon"]])
                                prev = transit_stop
                            connected_solutions.append((start_stop, end_stop, route, distance, trace, next_three_wait_times))

    return connected_solutions


def get_route_distance(route):
    prev, total_distance = None, 0
    for lat, lon in route:
        if prev:
            total_distance += haversine_distance(lat, lon, *prev)
        prev = (lat, lon)

    return total_distance

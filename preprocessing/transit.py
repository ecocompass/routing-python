import re

import pandas as pd
from tqdm import tqdm

from routing.core import haversine_distance


def compute_route_and_stops(gtfs_type):
    print("[TRANSIT COMPUTING ROUTE AND STOPS]")
    print(f"Reading '{gtfs_type}' GTFS files...")
    stops_df = pd.read_csv("data/" + gtfs_type + '_gtfs/stops.csv')
    trips_df = pd.read_csv("data/" + gtfs_type + '_gtfs/trips.csv')
    stop_times_df = pd.read_csv("data/" + gtfs_type + '_gtfs/stop_times.csv')
    routes_df = pd.read_csv("data/" + gtfs_type + '_gtfs/routes.csv')
    shapes_df = pd.read_csv("data/" + gtfs_type + '_gtfs/shapes.csv')
    print("Files read successfully. Processing data...")

    data_structure = {f"{gtfs_type}_stops": {}, f"{gtfs_type}_routes": {}, f"{gtfs_type}_shapes": {}}
    print(f"Adding '{gtfs_type}' stop entries.")
    for _, row in stops_df.iterrows():
        stop_id = row['stop_id']
        data_structure[f"{gtfs_type}_stops"][stop_id] = {
            "lat": row['stop_lat'],
            "lon": row['stop_lon'],
            "name": row['stop_name'],
            "routes": {}
        }

    print("Merging stop times, trips and routes into single table.")
    merged_df = stop_times_df.merge(trips_df, on='trip_id').merge(routes_df, on='route_id')

    print(f"Adding route timings to '{gtfs_type}' stops.", flush=True)
    for _, row in tqdm(merged_df.iterrows(), total=merged_df.shape[0], desc="Processing route timings"):
        stop_id = row['stop_id']
        route_short_name = row['route_short_name']
        service_id = row['service_id']

        if route_short_name not in data_structure[f"{gtfs_type}_stops"][stop_id]["routes"]:
            data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name] = {}

        if service_id not in data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name]:
            data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name][service_id] = []

        data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name][service_id].append(
            row['arrival_time'])

    print(f"\nAdding '{gtfs_type}' route entries.", flush=True)
    for _, row in tqdm(merged_df.iterrows(), total=merged_df.shape[0], desc="Processing route entries"):
        route_short_name = row['route_short_name']
        route_key = f"{route_short_name}_{row['direction_id']}"
        if route_key not in data_structure[f"{gtfs_type}_routes"]:
            data_structure[f"{gtfs_type}_routes"][route_key] = []
        if row['stop_id'] not in data_structure[f"{gtfs_type}_routes"][route_key]:
            data_structure[f"{gtfs_type}_routes"][route_key].append(row['stop_id'])

    # Processing shapes data
    # print(f"\nProcessing '{gtfs_type}' shapes.", flush=True)
    # for _, row in tqdm(shapes_df.iterrows(), total=shapes_df.shape[0], desc="Processing route shapes"):
    #     shape_id = row['shape_id']
    #     # Find a trip that uses this shape_id to get route_short_name and direction_id
    #     trip_row = trips_df[trips_df['shape_id'] == shape_id].iloc[0]
    #     route_short_name = routes_df[routes_df['route_id'] == trip_row['route_id']].iloc[0]['route_short_name']
    #     route_key = f"{route_short_name}_{trip_row['direction_id']}"
    #
    #     if route_key not in data_structure[f"{gtfs_type}_shapes"]:
    #         data_structure[f"{gtfs_type}_shapes"][route_key] = []
    #
    #     data_structure[f"{gtfs_type}_shapes"][route_key].append([row['shape_pt_lat'], row['shape_pt_lon']])
    #
    # # workaround to handle duplicate shapes in case of luas
    # if gtfs_type != "bus":
    #     print(f"\nWorkaround '{gtfs_type}' for shapes")
    #     for route_key in data_structure[f"{gtfs_type}_shapes"]:
    #         print("Processing route:", route_key)
    #         prev, proc_shape, proc_shapes = None, [], []
    #
    #         for coord in data_structure[f"{gtfs_type}_shapes"][route_key]:
    #             if prev:
    #                 d = haversine_distance(*prev, *coord)
    #                 if d > 10:
    #                     proc_shapes.append(proc_shape)
    #                     proc_shape = []
    #                     print("split", prev, coord, d)
    #                 else:
    #                     proc_shape.append(coord)
    #             prev = coord
    #
    #         # print("shape lengths")
    #         # for shape in proc_shapes:
    #         #     print("     ", len(shape))
    #         data_structure[f"{gtfs_type}_shapes"][route_key] = max(proc_shapes, key=len)

    # Processing shapes data
    if gtfs_type == "bus":
        print(f"\nProcessing '{gtfs_type}' shapes.", flush=True)
        # for route_id in data_structure[f"{gtfs_type}_routes"]

        for _, row in tqdm(routes_df.iterrows(), total=merged_df.shape[0], desc="Processing route entries"):
            route_short_name = row['route_short_name']
            route_id = row["route_id"]
            for direction_id in (0, 1):
                route_key = f"{route_short_name}_{direction_id}"

                print("------->", route_key)

                route_trips = trips_df[(trips_df['route_id'] == route_id) & (trips_df['direction_id'] == direction_id)]

                shape_id = route_trips.iloc[0]['shape_id']
                route_shape = shapes_df[shapes_df['shape_id'] == shape_id][['shape_pt_lat', 'shape_pt_lon']].values.tolist()
                data_structure[f"{gtfs_type}_shapes"][route_id] = route_shape

    return data_structure

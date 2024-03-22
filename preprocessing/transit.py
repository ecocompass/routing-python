import json
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

        # skip all rails other than dart
        if gtfs_type == "dart" and route_short_name != "DART":
            continue

        service_id = row['service_id']

        if route_short_name not in data_structure[f"{gtfs_type}_stops"][stop_id]["routes"]:
            data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name] = {}

        if service_id not in data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name]:
            data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name][service_id] = []

        data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name][service_id].append(
            row['arrival_time'])

    if gtfs_type == "dart":
        cleaned_stops = {}
        # cleaning up empty stops for DART
        for stop_id in data_structure[f"{gtfs_type}_stops"]:
            if data_structure[f"{gtfs_type}_stops"][stop_id]["routes"]:
                cleaned_stops[stop_id] = data_structure[f"{gtfs_type}_stops"][stop_id]

        data_structure[f"{gtfs_type}_stops"] = cleaned_stops


    print(f"\nAdding '{gtfs_type}' route entries.", flush=True)
    for _, row in tqdm(merged_df.iterrows(), total=merged_df.shape[0], desc="Processing route entries"):
        route_short_name = row['route_short_name']

        # skip all rails other than dart
        if gtfs_type == "dart" and route_short_name != "DART":
            continue

        route_key = f"{route_short_name}_{row['direction_id']}"
        if route_key not in data_structure[f"{gtfs_type}_routes"]:
            data_structure[f"{gtfs_type}_routes"][route_key] = []
        if row['stop_id'] not in data_structure[f"{gtfs_type}_routes"][route_key]:
            data_structure[f"{gtfs_type}_routes"][route_key].append(row['stop_id'])

    # Processing shapes data
    print(f"\nProcessing '{gtfs_type}' shapes.", flush=True)
    if gtfs_type == "luas":
        with open("data/.luas_shapes.workaround.json", "r") as file:
            luas_workaround = json.loads(file.read())

            for route_key in luas_workaround:
                data_structure[f"{gtfs_type}_shapes"][route_key] = luas_workaround[route_key]
    elif gtfs_type == "dart":
        with open("data/.dart_shapes.workaround.json", "r") as file:
            dart_workaround = json.loads(file.read())

            for route_key in dart_workaround:
                data_structure[f"{gtfs_type}_shapes"][route_key] = dart_workaround[route_key]

    else:
        shapes_df = pd.read_csv("data/" + gtfs_type + '_gtfs/shapes.csv')
        for _, row in tqdm(shapes_df.iterrows(), total=shapes_df.shape[0], desc="Processing route shapes"):
            shape_id = row['shape_id']
            # Find a trip that uses this shape_id to get route_short_name and direction_id
            trip_row = trips_df[trips_df['shape_id'] == shape_id].iloc[0]
            route_short_name = routes_df[routes_df['route_id'] == trip_row['route_id']].iloc[0]['route_short_name']

            route_key = f"{route_short_name}_{trip_row['direction_id']}"

            if route_key not in data_structure[f"{gtfs_type}_shapes"]:
                data_structure[f"{gtfs_type}_shapes"][route_key] = []

            data_structure[f"{gtfs_type}_shapes"][route_key].append([row['shape_pt_lat'], row['shape_pt_lon']])

    return data_structure

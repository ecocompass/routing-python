import pandas as pd


def compute_route_and_stops(gtfs_type):
    print("[TRANSIT COMPUTING ROUTE AND STOPS]")
    print(f"Reading '{gtfs_type}' GTFS files...")
    stops_df = pd.read_csv("data/" + gtfs_type + '_gtfs/stops.csv')
    trips_df = pd.read_csv("data/" + gtfs_type + '_gtfs/trips.csv')
    stop_times_df = pd.read_csv("data/" + gtfs_type + '_gtfs/stop_times.csv')
    routes_df = pd.read_csv("data/" + gtfs_type + '_gtfs/routes.csv')
    print("Files read successfully. Processing data...")

    data_structure = {f"{gtfs_type}_stops": {}, f"{gtfs_type}_routes": {}}
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
    print(f"Adding route timings to '{gtfs_type}' stops.")
    for _, row in merged_df.iterrows():
        stop_id = row['stop_id']
        route_short_name = row['route_short_name']
        service_id = row['service_id']

        if route_short_name not in data_structure[f"{gtfs_type}_stops"][stop_id]["routes"]:
            data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name] = {}

        if service_id not in data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name]:
            data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name][service_id] = []

        data_structure[f"{gtfs_type}_stops"][stop_id]["routes"][route_short_name][service_id].append(
            row['arrival_time'])

    print(f"Adding '{gtfs_type}' route entries.")
    for _, row in merged_df.iterrows():
        route_short_name = row['route_short_name']
        route_key = f"{route_short_name}_{row['direction_id']}"
        if route_key not in data_structure[f"{gtfs_type}_routes"]:
            data_structure[f"{gtfs_type}_routes"][route_key] = []
        if row['stop_id'] not in data_structure[f"{gtfs_type}_routes"][route_key]:
            data_structure[f"{gtfs_type}_routes"][route_key].append(row['stop_id'])

    return data_structure

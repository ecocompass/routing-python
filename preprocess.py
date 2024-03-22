import common
import preprocessing.overpass as overpass
import preprocessing.road as road
import preprocessing.transit as transit

import json


def main():
    geo_map = {"country": "IE", "county": "County Dublin"}
    response = overpass.query_location(geo_map)
    with open(common.road_raw_data_file_name, "wb") as file:
        file.write(response)

    consolidated_data = {}
    for gtfs_type in common.gtfs_types:
        consolidated_data.update(transit.compute_route_and_stops(gtfs_type))

    print(f"Saving consolidated transit data to '{common.consolidated_gtfs_file_name}'")
    with open(common.consolidated_gtfs_file_name, "w", encoding="utf-8") as file:
        file.write(json.dumps(consolidated_data))

    road_adj = road.compute_road_adjacency_map(common.road_raw_data_file_name)
    print(f"Saving processed road adjacency data to '{common.road_processed_data_file_name}'")
    with open(common.road_processed_data_file_name, "w", encoding="utf-8") as file:
        file.write(json.dumps(road_adj))


if __name__ == "__main__":
    main()
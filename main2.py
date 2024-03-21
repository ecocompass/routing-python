import time

import common
import geojson
from routing import query as routing_query

query = routing_query.Query(common.consolidated_gtfs_file_name, common.road_processed_data_file_name)

start_time = time.time()

# start = 53.324656, -6.274100 # home rathmines
# start = 53.315176, -6.281835
# end = 53.343915, -6.254582  # trinity
# end = 53.254836, -6.112460 # killiney beach
end = 53.425014, -6.235733 # airport
start = 53.254836, -6.112460 # killiney beach

sols = query.get_route_options(start, end)

color_map = {
    "bus": "orange",
    "luas": "green",
    "walk": "blue"
}


# sort segments by walk distance
sols_bus_luas_sorted = sorted(sols["bus-luas"], key=lambda sol: sol["distance_walk"])
sols_bus_shrink_sorted = sorted(sols["bus-shrink"], key=lambda sol: sol["distance_walk"])
sols_bus_split_sorted = sorted(sols["bus-split"], key=lambda sol: sol["distance_walk"])
sols_sorted = [sols_bus_luas_sorted[0], sols_bus_shrink_sorted[0], sols_bus_split_sorted[0]]

for i in range(0, min(3, len(sols_sorted))):
    geojson_builder = geojson.GeoJSONBuilder()
    for segment in sols_sorted[i]["segments"]:
        geojson_builder.add_line(color_map[segment["type"]], [(lon, lat) for lat, lon in segment["path"]])

    with open(f"geojson_{i}.json", "w") as file:
        file.write(geojson_builder.to_string())

print("Total time taken:", time.time() - start_time)

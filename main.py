import common
import geojson
from routing import query as routing_query
from routing import core as routing_core


query = routing_query.Query(common.consolidated_gtfs_file_name, common.road_processed_data_file_name)

start = 53.324656, -6.274100
# end = 53.343915, -6.254582  # trinity
end = 53.425014, -6.235733 # airport

ans = query.bus_walking_route(start, end)

"""
        return {
            "start": start,
            "end": end,
            "start_stop": start_stop,
            "end_stop": end_stop,
            "bus": {
                "label": route_label,
                "distance": distance,
                "trace": trace,
                "wait_time": wait_time,
                "transit_time": ans_transit_time,
            },
            "walk_start": ans_walking_route_start,
            "walk_end": ans_walking_route_end,
        }
"""

print("[Generating GEOJSON String]")
geojson_str = geojson.get_geojson(
    start[::-1], end[::-1],
    ans["bus"]["start_stop"][::-1],
    ans["bus"]["end_stop"][::-1],
    [(coord[1], coord[0]) for coord in ans["walk_start"]],
    [(coord[1], coord[0]) for coord in ans["bus"]["trace"]],
    [(coord[1], coord[0]) for coord in ans["walk_end"]],
)

print(geojson_str)
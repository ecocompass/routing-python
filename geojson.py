import json


def get_geojson(start_coordinate, end_coordinate, bus_start_coordinate, bus_end_coordinate,
                start_walk_route, bus_route, end_walk_route):
    with open("data/geojson-template", "r") as file:
        template = file.read()

        geojson_str = template.replace("{start_coordinate}", json.dumps(start_coordinate))
        geojson_str = geojson_str.replace("{end_coordinate}", json.dumps(end_coordinate))
        geojson_str = geojson_str.replace("{bus_start_coordinate}", json.dumps(bus_start_coordinate))
        geojson_str = geojson_str.replace("{bus_end_coordinate}", json.dumps(bus_end_coordinate))
        geojson_str = geojson_str.replace("{bus_route}", json.dumps(bus_route))
        geojson_str = geojson_str.replace("{start_walk_route}", json.dumps(start_walk_route))
        geojson_str = geojson_str.replace("{end_walk_route}", json.dumps(end_walk_route))

        return geojson_str
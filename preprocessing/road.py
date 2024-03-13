import json


def compute_road_adjacency_map(source_file):
    print("[ROAD COMPUTING ADJACENCY MAP]")
    with open(source_file, "r", encoding="utf-8") as file:
        data = json.loads(file.read())

    nodes = {}
    for element in data["elements"]:
        if element["type"] == "node":
            node_id = str(element["id"])
            nodes[node_id] = {
                "lat": element["lat"],
                "lon": element["lon"],
                "neighbors": set(),
            }
            if "tags" in element and "name" in element["tags"]:
                nodes[node_id]["name"] = element["tags"]["name"]
            else:
                nodes[node_id]["name"] = None

        if element["type"] == "way":
            last_node_id = None
            for node in element["nodes"]:
                node_id = str(node)
                if last_node_id:
                    nodes[node_id]["neighbors"].add(last_node_id)
                    nodes[last_node_id]["neighbors"].add(node_id)
                last_node_id = node_id

    for node in nodes:
        nodes[node]["neighbors"] = list(nodes[node]["neighbors"])

    return nodes
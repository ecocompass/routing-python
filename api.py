import common
from flask import Flask, request, jsonify
from routing import query as routing_query


app = Flask(__name__)
query = routing_query.Query(common.consolidated_gtfs_file_name, common.road_processed_data_file_name)


@app.route('/api/routes', methods=['GET'])
def get_routes():
    # Extract start and end coordinates from the query parameters
    start_coordinates = request.args.get('startCoordinates', '')
    end_coordinates = request.args.get('endCoordinates', '')

    start_coordinates = start_coordinates.split(",")
    start_coordinates = float(start_coordinates[0]), float(start_coordinates[1])

    end_coordinates = end_coordinates.split(",")
    end_coordinates = float(end_coordinates[0]), float(end_coordinates[1])

    sols = query.get_route_options(start_coordinates, end_coordinates)
    sols_bus_luas_sorted = sorted(sols["bus-luas"], key=lambda sol: sol["distance_walk"])
    sols_bus_shrink_sorted = sorted(sols["bus-shrink"], key=lambda sol: sol["distance_walk"])
    sols_bus_split_sorted = sorted(sols["bus-split"], key=lambda sol: sol["distance_walk"])
    sols_sorted = [sols_bus_luas_sorted[0], sols_bus_shrink_sorted[0], sols_bus_split_sorted[0]]

    return jsonify(sols_sorted)

    # return jsonify(route_info)


if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=8989, debug=True)
import common
from flask import Flask, request, jsonify
from routing import query as routing_query


app = Flask(__name__)
query = routing_query.Query(common.consolidated_gtfs_file_name, common.road_processed_data_file_name)


@app.route('/api/routes', methods=['GET'])
@app.route('/routes', methods=['GET'])
@app.route('/route', methods=['GET'])
def get_routes():
    # Extract start and end coordinates from the query parameters
    start_coordinates = request.args.get('startCoordinates', '')
    end_coordinates = request.args.get('endCoordinates', '')

    try:
        start_coordinates = start_coordinates.split(",")
        start_coordinates = float(start_coordinates[1]), float(start_coordinates[0]) # lon, lat -> lat, lon
    except Exception as e:
        return jsonify({"error_message": "Incorrect format for startCoordinates", "error": str(e)})

    try:
        end_coordinates = end_coordinates.split(",")
        end_coordinates = float(end_coordinates[1]), float(end_coordinates[0]) # lon, lat -> lat, lon
    except Exception as e:
        return jsonify({"error_message": "Incorrect format for endCoordinates", "error": str(e)})

    try:
        sols = query.get_route_options(start_coordinates, end_coordinates)
        sols_bus_luas_sorted = sorted(sols["bus-luas"], key=lambda sol: sol["distance_walk"])
        sols_bus_shrink_sorted = sorted(sols["bus-shrink"], key=lambda sol: sol["distance_walk"])
        sols_bus_split_sorted = sorted(sols["bus-split"], key=lambda sol: sol["distance_walk"])
        sols_sorted = [sols_bus_luas_sorted[0], sols_bus_shrink_sorted[0], sols_bus_split_sorted[0]]
        return jsonify(sols_sorted)
    except Exception as e:
        return jsonify({"error_message": "Issuse while computing routes", "error": str(e)})

    

    # return jsonify(route_info)


if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=8080, debug=True)
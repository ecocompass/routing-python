gtfs_types = [
    "bus",
    "dart",
    "luas"
]
consolidated_gtfs_file_name = "data/consolidated_gtfs.json"
road_raw_data_file_name = "data/.road_overpass.json"
road_processed_data_file_name = "data/road_map.json"

average_speeds = {
    "walking": 4,
    "bus": 15,
    "luas": 25,
    "dart": 60
}

service_id_mappings = {
    "luas": {
        0: [129, 132],
        1: [129, 132],
        2: [129, 132],
        3: [129, 132],
        4: [129, 131, 132],
        5: [130],
        6: [132],
    },
    "bus": {
        0: [270, 360],
        1: [270, 360],
        2: [270, 360],
        3: [270, 360],
        4: [270, 360],
        5: [61, 361],
        6: [362],
    },
    "dart": {0: [319,
                 320,
                 332,
                 339,
                 342,
                 343,
                 345,
                 346,
                 348,
                 350,
                 351,
                 352,
                 356,
                 359,
                 360,
                 361,
                 363,
                 364,
                 365,
                 366,
                 367,
                 370,
                 371],
             1: [58,
                 320,
                 332,
                 339,
                 342,
                 343,
                 345,
                 346,
                 348,
                 350,
                 351,
                 352,
                 356,
                 359,
                 360,
                 361,
                 363,
                 364,
                 365,
                 366,
                 368,
                 370,
                 371],
             2: [320,
                 332,
                 339,
                 342,
                 343,
                 345,
                 346,
                 348,
                 350,
                 351,
                 352,
                 356,
                 359,
                 360,
                 361,
                 363,
                 364,
                 365,
                 366,
                 368,
                 370,
                 371],
             3: [57,
                 320,
                 332,
                 339,
                 342,
                 343,
                 345,
                 346,
                 348,
                 350,
                 351,
                 352,
                 356,
                 359,
                 360,
                 361,
                 363,
                 364,
                 365,
                 366,
                 368,
                 370,
                 371],
             4: [56,
                 320,
                 332,
                 339,
                 342,
                 343,
                 345,
                 346,
                 348,
                 349,
                 359,
                 360,
                 362,
                 363,
                 364,
                 365,
                 366,
                 368,
                 369,
                 371],
             5: [20,
                 59,
                 321,
                 333,
                 334,
                 336,
                 337,
                 338,
                 343,
                 346,
                 347,
                 348,
                 350,
                 351,
                 359,
                 360,
                 363,
                 364,
                 365,
                 366,
                 369,
                 370,
                 371],
             6: [81, 162, 318, 325, 344, 358]}
}

k_nearest_mappings = {
    "bus": 15,
    "dart": 5,
    "luas": 5
}
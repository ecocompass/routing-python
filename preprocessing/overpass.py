import requests


def query_location(geo_map):
    print("[OVERPASS QUERY LOCATION]")
    overpass_url = "https://overpass-api.de/api/interpreter"
    vars_string = ""
    geofilter_string = "(way"

    if "country" in geo_map:
        vars_string += f"area[\"ISO3166-1:alpha2\"=\"{geo_map['country']}\"]->.country;"
        geofilter_string += "(area.country)"

    if "county" in geo_map:
        vars_string += f"area[\"admin_level\"=\"6\"][\"name\"=\"{geo_map['county']}\"]->.county;"
        geofilter_string += "(area.county)"

    if "city" in geo_map:
        vars_string += f"area[\"admin_level\"=\"7\"][\"name\"=\"{geo_map['city']}\"]->.city;"
        geofilter_string += "(area.city)"

    if "neighborhood" in geo_map:
        vars_string += f"area[\"name\"=\"{geo_map['neighborhood']}\"]->.neighborhood;"
        geofilter_string += "(area.neighborhood)"

    query_string = "[out:json];" + vars_string + geofilter_string + "[highway];>;);out body;"

    print("SENDING REQUEST TO: " + overpass_url)
    print("QUERY STRING\n" + query_string)

    response = requests.get(overpass_url, params={'data': query_string})

    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code}\n{response.text}")
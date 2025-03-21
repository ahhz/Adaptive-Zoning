import pyproj
import requests
import polyline

def bng_to_wgs84(bng_points):
    """
    Converts a list of British National Grid (BNG) points to WGS 84 coordinates using pyproj.

    Args:
        bng_points (list of tuples): A list of (eastings, northings) tuples in BNG.

    Returns:
        list of tuples: A list of (longitude, latitude) tuples in WGS 84.
    """

    # Define the BNG and WGS 84 CRSs
    bng_crs = pyproj.CRS("EPSG:27700")
    wgs84_crs = pyproj.CRS("EPSG:4326")

    # Create a Transformer object
    transformer = pyproj.Transformer.from_crs(bng_crs, wgs84_crs, always_xy=True)

    # Transform the coordinates
    wgs84_points = [transformer.transform(easting, northing) for easting, northing in bng_points]

    return wgs84_points

def get_distance_wgs84_lon_lat(a,b):
    return pyproj.Geod(ellps="WGS84").line_length(*([ca,cb] for ca,cb in zip(a,b)))

def get_halfway_distance(origin, destination, mode, openroute_api_key, first_half = True):
    """
    Calculates the halfway distance and duration along a route using OpenRouteService API.

    Args:
        origin (tuple): Tuple representing the origin coordinates (longitude, latitude).
        destination (tuple): Tuple representing the destination coordinates (longitude, latitude).
        mode (str): The routing mode (e.g., 'driving-car', 'foot-walking', 'cycling-regular').

    Returns:
        tuple: (running_distance, running_duration) if successful, or None if an error occurs.
    """
    if origin == destination: return {"distance" : 0, "duration" : 0}
    
    base_url = "https://api.openrouteservice.org/v2/directions"
    url = base_url + "/" + mode

    data = {
        "coordinates": [[origin[0], origin[1]], [destination[0], destination[1]]]
    }

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': openroute_api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    
        response_data = response.json()
    
        if 'routes' not in response_data or not response_data['routes']:
            print("Error: No routes found in the API response.")
            return {"distance" : None, "duration" : None}

        route = response_data['routes'][0]
    
        if 'geometry' not in route or 'summary' not in route or 'segments' not in route:
            print("Error: Incomplete route data in the API response.")
            return {"distance" : None, "duration" : None}
    
        encoded_geometry = route['geometry']
        points = polyline.decode(encoded_geometry)
    
        total_distance = route['summary']['distance']
        total_duration = route['summary']['duration']
    
        halfway_euclidean = 0.5 * get_distance_wgs84_lon_lat(points[0], points[-1])
        print("halfway ; ", halfway_euclidean)
        running_distance = 0
        running_duration = 0
    
        for segment in route['segments']:
            if 'steps' not in segment:
                print("Warning: Segment missing 'steps'. Skipping.")
                continue
    
            for step in segment['steps']:
                if 'way_points' not in step or 'distance' not in step or 'duration' not in step:
                    print("Warning: Step missing required data. Skipping.")
                    continue
    
                step_end = step['way_points'][-1]
                euclidean_end = get_distance_wgs84_lon_lat(points[0], points[step_end])
    
                if len(step['way_points']) == 0:
                    print("Warning: step waypoints is empty. Skipping")
                    continue
    
                step_start = step['way_points'][0]
                euclidean_start = get_distance_wgs84_lon_lat(points[0], points[step_start])
    
                if euclidean_end > halfway_euclidean:
                    
                    part = (halfway_euclidean - euclidean_start) / (euclidean_end - euclidean_start)
                    running_distance += part * step['distance']
                    running_duration += part * step['duration']
                    if first_half:
                        return {"distance" : running_distance, "duration": running_duration}
                    else:
                        return {"distance" : total_distance - running_distance, 
                                "duration" : total_duration - running_duration}
                    
                running_distance +=  step['distance']
                running_duration +=  step['duration']

        print("Error: Halfway point not found within route segments.")
        return {"distance" : None, "duration" : None}

    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed - {e}")
        return {"distance" : None, "duration" : None}
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error: Problem parsing API response - {e}")
        return {"distance" : None, "duration" : None}
    except polyline.DecodeError as e:
        print(f"Error: Could not decode polyline - {e}")
        return {"distance" : None, "duration" : None}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"distance" : None, "duration" : None}


def get_full_distance(origin, destination, mode,openroute_api_key):
    """
    Calculates the halfway distance and duration along a route using OpenRouteService API.

    Args:
        origin (tuple): Tuple representing the origin coordinates (longitude, latitude).
        destination (tuple): Tuple representing the destination coordinates (longitude, latitude).
        mode (str): The routing mode (e.g., 'driving-car', 'foot-walking', 'cycling-regular').

    Returns:
        tuple: (running_distance, running_duration) if successful, or None if an error occurs.
    """
    if origin == destination: return {"distance" : 0, "duration" : 0}
    base_url = "https://api.openrouteservice.org/v2/directions"
    url = base_url + "/" + mode

    data = {
        "coordinates": [[origin[0], origin[1]], [destination[0], destination[1]]]
    }

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': openroute_api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    
        response_data = response.json()
    
        if 'routes' not in response_data or not response_data['routes']:
            print("Error: No routes found in the API response.")
            return {"distance" : None, "duration" : None}

        route = response_data['routes'][0]
    
        if 'geometry' not in route or 'summary' not in route or 'segments' not in route:
            print("Error: Incomplete route data in the API response.")
            return {"distance" : None, "duration" : None}
    
        encoded_geometry = route['geometry']
        points = polyline.decode(encoded_geometry)
    
        total_distance = route['summary']['distance']
        total_duration = route['summary']['duration']
        return {"distance" : total_distance, "duration" : total_duration}
        
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed - {e}")
        return {"distance" : None, "duration" : None}
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error: Problem parsing API response - {e}")
        return {"distance" : None, "duration" : None}
    except polyline.DecodeError as e:
        print(f"Error: Could not decode polyline - {e}")
        return {"distance" : None, "duration" : None}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"distance" : None, "duration" : None}

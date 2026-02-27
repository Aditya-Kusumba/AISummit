import osmnx as ox
import networkx as nx
import os

GRAPH_FILE = "roads.graphml"
G = None


def load_or_build_graph(center_lat, center_lon):
    global G

    if os.path.exists(GRAPH_FILE):
        G = ox.load_graphml(GRAPH_FILE)
    else:
        G = ox.graph_from_point(
            (center_lat, center_lon),
            dist=20000,           # 20km radius (adjust if needed)
            network_type="drive"
        )
        ox.save_graphml(G, GRAPH_FILE)


def nearest_node(lat, lon):
    return ox.distance.nearest_nodes(G, lon, lat)


def road_distance(v1, v2):
    n1 = nearest_node(v1.latitude, v1.longitude)
    n2 = nearest_node(v2.latitude, v2.longitude)

    return nx.shortest_path_length(G, n1, n2, weight="length")


def generate_osm_route(villages):

    global G

    if G is None:
        load_or_build_graph(
            villages[0].latitude,
            villages[0].longitude
        )

    route = [villages[0]]
    unvisited = villages[1:]
    total_distance = 0

    while unvisited:
        last = route[-1]

        next_village = min(
            unvisited,
            key=lambda v: road_distance(last, v)
        )

        distance = road_distance(last, next_village)
        total_distance += distance

        route.append(next_village)
        unvisited.remove(next_village)

    # Convert meters → km
    total_distance_km = total_distance / 1000

    # Assume rural avg speed = 35 km/h
    avg_speed_kmph = 35
    travel_time_minutes = (total_distance_km / avg_speed_kmph) * 60

    # Treatment time assumption: 30 mins per village
    treatment_time_minutes = len(route) * 30

    total_mission_time = travel_time_minutes + treatment_time_minutes

    return {
        "mode": "osm",
        "route_sequence": [v.id for v in route],
        "total_distance_km": round(total_distance_km, 2),
        "travel_time_minutes": round(travel_time_minutes, 1),
        "treatment_time_minutes": treatment_time_minutes,
        "total_mission_time_minutes": round(total_mission_time, 1)
    }
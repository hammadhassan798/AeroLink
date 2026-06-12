from DL.airport_service import get_airports
from Datastructures.graph import *
from DL.route_service import get_routes

def build_route_graph():
    graph = RouteGraph()
    routes = get_routes()
    for r in routes:
        graph.add_edge(
            r['from_airport'],
            r['to_airport'],
            r['route_id']
        )
    return graph
class RouteGraph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, from_airport, to_airport, route_id):
        if from_airport not in self.graph:
            self.graph[from_airport] = []
        self.graph[from_airport].append({
            "to": to_airport,
            "route_id": route_id
        })

    def get_next_routes(self, from_airport):
        return self.graph.get(from_airport, [])
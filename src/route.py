import pandas as pd
import networkx as nx
import random


class RouteManager:
    def __init__(self, routes_file='data/routes.csv', airports_file='data/airports.csv',
                 output_file='data/country_routes_min_2_stops.csv'):
        self.routes_file = routes_file
        self.airports_file = airports_file
        self.output_file = output_file
        self.graph = None
        self.countries = None

        # Load data and build graph
        self._load_data()
        self._build_country_graph()

    def _load_data(self):
        """Load route and airport data from CSV files"""
        df = pd.read_csv(self.routes_file)
        df2 = pd.read_csv(self.airports_file)

        self.routes_df = df[["Source airport", "Destination airport"]]
        self.airports_df = df2[["Country", "City", "IATA"]]
        self.airport_to_country = dict(zip(self.airports_df["IATA"], self.airports_df["Country"]))

    def _build_country_graph(self):
        """Build a directed graph at the country level"""
        self.graph = nx.DiGraph()

        # Add edges based on flights, using countries instead of airports
        for _, row in self.routes_df.iterrows():
            source_airport = row["Source airport"]
            dest_airport = row["Destination airport"]

            # Get corresponding countries
            source_country = self.airport_to_country.get(source_airport)
            dest_country = self.airport_to_country.get(dest_airport)

            # Ensure valid mapping and avoid self-loops
            if source_country and dest_country and source_country != dest_country:
                self.graph.add_edge(source_country, dest_country)

        # Store list of countries
        self.countries = list(self.graph.nodes)

    def find_routes_with_min_stops(self, min_path_length=2):
        """Find country pairs with path length >= min_path_length"""
        routes_with_min_stops = []

        for source in self.graph.nodes:
            for target in self.graph.nodes:
                if source != target:  # Avoid self-loops
                    try:
                        path_length = nx.shortest_path_length(self.graph, source=source, target=target)
                        if path_length >= min_path_length:
                            routes_with_min_stops.append((source, target, path_length))
                    except nx.NetworkXNoPath:
                        continue  # No path exists between these countries

        # Convert results to DataFrame and save
        result_df = pd.DataFrame(routes_with_min_stops,
                                 columns=["Source Country", "Destination Country", "Path Length"])
        result_df.to_csv(self.output_file, index=False)

        return result_df

    def pick_random_route(self, min_path_length=3):
        """Pick a random source and destination with path length >= min_path_length"""
        valid_pairs = []

        for source in self.graph.nodes:
            for target in self.graph.nodes:
                if source != target:  # Avoid self-loops
                    try:
                        path_length = nx.shortest_path_length(self.graph, source=source, target=target)
                        if path_length >= min_path_length:
                            valid_pairs.append((source, target))
                    except nx.NetworkXNoPath:
                        continue  # No path exists between these countries

        if not valid_pairs:
            return None, None

        source, destination = random.choice(valid_pairs)
        correct_path = nx.shortest_path(self.graph, source=source, target=destination)

        return source, destination, correct_path

    def get_neighbors(self, country):
        """Get neighboring countries"""
        if country in self.graph:
            return list(self.graph.neighbors(country))
        return []

    def check_valid_move(self, current_country, next_country):
        """Check if a move from current_country to next_country is valid"""
        return next_country in self.get_neighbors(current_country)


# If run directly, generate the CSV file
if __name__ == "__main__":
    route_manager = RouteManager()
    route_manager.find_routes_with_min_stops(min_path_length=3)
    print(f"Country-to-country routes with at least 3 flights saved to '{route_manager.output_file}'.")
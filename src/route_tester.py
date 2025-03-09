import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from route import RouteManager
import sys


def show_shortest_path(source, destination, route_manager):
    """Display the shortest path between source and destination countries"""
    if source not in route_manager.countries:
        print(f"Error: Source country '{source}' not found in graph.")
        return False

    if destination not in route_manager.countries:
        print(f"Error: Destination country '{destination}' not found in graph.")
        return False

    try:
        path = nx.shortest_path(route_manager.graph, source=source, target=destination)
        path_length = len(path) - 1

        print(f"\nShortest path from {source} to {destination}:")
        print(" → ".join(path))
        print(f"Path length: {path_length} (requires {path_length} flights)")

        return True
    except nx.NetworkXNoPath:
        print(f"No path exists from {source} to {destination}.")
        return False


def plot_path(source, destination, route_manager):
    """Plot the shortest path between source and destination countries"""
    try:
        path = nx.shortest_path(route_manager.graph, source=source, target=destination)

        # Create a subgraph with the path edges
        path_edges = list(zip(path[:-1], path[1:]))
        path_graph = route_manager.graph.edge_subgraph(path_edges)

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(path_graph, seed=42)

        # Draw the graph
        nx.draw(path_graph, pos, with_labels=True, node_color='lightblue',
                node_size=1500, font_size=10, font_weight='bold',
                arrows=True, arrowsize=20, edge_color='gray')

        # Draw path edges in red
        nx.draw_networkx_edges(path_graph, pos, edgelist=path_edges,
                               width=2, edge_color='red', arrows=True, arrowsize=20)

        plt.title(f"Shortest Path from {source} to {destination}")
        plt.tight_layout()
        plt.savefig(f"{source}_to_{destination}_path.png")
        print(f"Path visualization saved as '{source}_to_{destination}_path.png'")

        plt.show()
        return True
    except nx.NetworkXNoPath:
        print(f"No path exists from {source} to {destination}.")
        return False
    except Exception as e:
        print(f"Error plotting path: {e}")
        return False


def find_paths_with_exact_length(route_manager, exact_length=3):
    """Find paths with exactly the specified length"""
    paths_with_exact_length = []

    for source in route_manager.countries:
        for target in route_manager.countries:
            if source != target:
                try:
                    path = nx.shortest_path(route_manager.graph, source=source, target=target)
                    path_length = len(path) - 1
                    if path_length == exact_length:
                        paths_with_exact_length.append((source, target, path))
                except nx.NetworkXNoPath:
                    continue

    return paths_with_exact_length


def list_random_examples(route_manager, count=5, min_length=2, max_length=5):
    """List random example routes with path lengths in the specified range"""
    import random

    # Find all paths within the length range
    valid_paths = []

    for source in route_manager.countries:
        for target in route_manager.countries:
            if source != target:
                try:
                    path_length = nx.shortest_path_length(route_manager.graph, source=source, target=target)
                    if min_length <= path_length <= max_length:
                        valid_paths.append((source, target, path_length))
                except nx.NetworkXNoPath:
                    continue

    # Sample random paths
    if not valid_paths:
        print(f"No paths found with length between {min_length} and {max_length}.")
        return []

    sample_size = min(count, len(valid_paths))
    samples = random.sample(valid_paths, sample_size)

    print(f"\nRandom examples of routes with path length between {min_length} and {max_length}:")
    for source, target, length in samples:
        path = nx.shortest_path(route_manager.graph, source=source, target=target)
        print(f"{source} to {target} (length {length}): {' → '.join(path)}")

    return samples


def print_route_statistics(route_manager):
    """Print statistics about the routes graph"""
    print("\nRoute Statistics:")
    print(f"Total countries: {len(route_manager.countries)}")
    print(f"Total connections: {route_manager.graph.number_of_edges()}")

    # Count paths of different lengths
    path_lengths = {}
    max_processed = 1000  # Limit to avoid excessive processing
    processed = 0

    for source in route_manager.countries:
        if processed >= max_processed:
            break

        for target in route_manager.countries:
            if source != target:
                try:
                    path_length = nx.shortest_path_length(route_manager.graph, source=source, target=target)
                    path_lengths[path_length] = path_lengths.get(path_length, 0) + 1
                    processed += 1
                    if processed >= max_processed:
                        break
                except nx.NetworkXNoPath:
                    continue

    print("\nPath length distribution (based on sample):")
    for length in sorted(path_lengths.keys()):
        print(f"  Length {length}: {path_lengths[length]} paths")

    # Countries with most connections
    out_degrees = dict(route_manager.graph.out_degree())
    top_sources = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]

    print("\nTop 5 source countries (most outgoing flights):")
    for country, count in top_sources:
        print(f"  {country}: {count} destinations")

    in_degrees = dict(route_manager.graph.in_degree())
    top_destinations = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]

    print("\nTop 5 destination countries (most incoming flights):")
    for country, count in top_destinations:
        print(f"  {country}: {count} sources")


def main():
    # Initialize RouteManager
    route_manager = RouteManager()

    # Print menu and process commands
    while True:
        print("\n=== Route Tester Menu ===")
        print("1. Check shortest path between countries")
        print("2. Find random examples of paths with specific length range")
        print("3. Visualize a path between countries")
        print("4. Show route statistics")
        print("5. Find paths with exact length")
        print("0. Exit")

        choice = input("\nEnter your choice (0-5): ")

        if choice == '0':
            print("Exiting Route Tester. Goodbye!")
            break

        elif choice == '1':
            source = input("Enter source country: ")
            destination = input("Enter destination country: ")
            show_shortest_path(source, destination, route_manager)

        elif choice == '2':
            min_length = int(input("Enter minimum path length: ") or "2")
            max_length = int(input("Enter maximum path length: ") or "5")
            count = int(input("Enter number of examples to show: ") or "5")
            list_random_examples(route_manager, count, min_length, max_length)

        elif choice == '3':
            source = input("Enter source country: ")
            destination = input("Enter destination country: ")
            if show_shortest_path(source, destination, route_manager):
                plot_path(source, destination, route_manager)

        elif choice == '4':
            print_route_statistics(route_manager)

        elif choice == '5':
            exact_length = int(input("Enter exact path length to find: ") or "3")
            paths = find_paths_with_exact_length(route_manager, exact_length)

            if not paths:
                print(f"No paths found with exactly {exact_length} stops.")
            else:
                print(f"\nFound {len(paths)} paths with exactly {exact_length} stops:")
                for i, (source, target, path) in enumerate(paths[:10], 1):
                    print(f"{i}. {source} to {target}: {' → '.join(path)}")

                if len(paths) > 10:
                    print(f"... and {len(paths) - 10} more")

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Check if matplotlib is available
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib is not installed. Path visualization will not be available.")
        print("Install it with: pip install matplotlib")

    main()
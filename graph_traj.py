import pandas as pd
from datetime import datetime
from collections import defaultdict
import networkx as nx
from geopy.distance import geodesic
 
 
 
stops = pd.read_csv('stops.txt')
stop_times = pd.read_csv('stop_times.txt', dtype=str, low_memory=False)
 
 
def parse_time(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s
 
stop_times = stop_times.sort_values(['trip_id', 'stop_sequence'])
 
edges = []
 
for trip_id, group in stop_times.groupby('trip_id'):
    group = group.sort_values('stop_sequence')
    stops_list = group['stop_id'].tolist()
    times = group['departure_time'].map(parse_time).tolist()
 
    for i in range(len(stops_list) - 1):
        u = str(stops_list[i])
        v = str(stops_list[i+1])
        duration = times[i+1] - times[i]
        if duration >= 0:
            edges.append((u, v, duration))
 
 
 
durations = defaultdict(list)
 
for u, v, d in edges:
    durations[(u, v)].append(d)
 
durations = { (u, v): sum(ds)/len(ds) for (u,v), ds in durations.items() }
 
 
G = nx.DiGraph()
 
for _, row in stops.iterrows():
    G.add_node(row['stop_id'], name=row['stop_name'], lat=row['stop_lat'], lon=row['stop_lon'])
 
for (u, v), d in durations.items():
    G.add_edge(u, v, weight=d)
 
 
 
 
G.remove_nodes_from(list(nx.isolates(G)))
stops = pd.DataFrame({'stop_id' : [str(n) for n in G.nodes] }).merge(stops,on = 'stop_id')
 
 
 
def stops_within_radius(lat, lon, radius_m=300):
    nearby_stops = []
    for _, row in stops.iterrows():
        dist = geodesic((lat, lon), (row['stop_lat'], row['stop_lon'])).meters
        if dist <= radius_m:
            nearby_stops.append(row['stop_id'])
    return nearby_stops
 
 
nearest_stops  = stops_within_radius(44.91414900,-0.74211900)
 
 
 
 
 
 
def reachable_stops(G, start_stops, max_duration=1800):
    import heapq
 
    visited = {}
    heap = []
 
    for stop_id in start_stops:
        heapq.heappush(heap, (0, stop_id))  # (cumulative_time, stop)
 
    while heap:
        current_time, u = heapq.heappop(heap)
        if u in visited and visited[u] <= current_time:
            continue
        visited[u] = current_time
 
        for v in G.successors(u):
            edge_time = G[u][v]['weight']
            total_time = current_time + edge_time
            if total_time <= max_duration:
                heapq.heappush(heap, (total_time, v))

    # After the while loop, print the farthest point visited
    if visited:
        farthest_stop = max(visited, key=lambda k: visited[k])
        print(f"Farthest stop: {farthest_stop} at {visited[farthest_stop]} seconds from start")
    print(f"Visited {len(visited)} stops within {max_duration} seconds.")
    return visited  # stop_id -> time in seconds
 
reachable = reachable_stops(G,nearest_stops)
 
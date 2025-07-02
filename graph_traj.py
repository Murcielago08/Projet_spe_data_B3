import pandas as pd
from datetime import datetime
from collections import defaultdict
import networkx as nx
 
 
 
stops = pd.read_csv('stops.txt')
stop_times = pd.read_csv('stop_times.txt')
 
 
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
        u = stops_list[i]
        v = stops_list[i+1]
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
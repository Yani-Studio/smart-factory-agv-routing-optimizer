import csv
import math
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model():
    data = {}
    walls = []
    with open('walls.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            walls.append({
                'id': int(row['id']),
                'x_min': int(row['x_min']),
                'x_max': int(row['x_max']),
                'y_min': int(row['y_min']),
                'y_max': int(row['y_max'])
            })
    data['walls'] = walls

    G = nx.grid_2d_graph(101, 101) 
    for w in walls:
        for x in range(w['x_min'], w['x_max'] + 1):
            for y in range(w['y_min'], w['y_max'] + 1):
                if (x, y) in G:
                    G.remove_node((x, y))
    data['G'] = G

    locations = []
    with open('locations.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append({
                'node_id': int(row['node_id']),
                'x': int(float(row['x'])),
                'y': int(float(row['y']))
            })
    data['locations'] = locations
    
    num_nodes = len(locations)
    distance_matrix = [[0] * num_nodes for _ in range(num_nodes)]
    
    for i in range(num_nodes):
        source_pos = (locations[i]['x'], locations[i]['y'])
        lengths = nx.single_source_dijkstra_path_length(G, source_pos)
        for j in range(num_nodes):
            if i != j:
                target_pos = (locations[j]['x'], locations[j]['y'])
                distance_matrix[i][j] = lengths.get(target_pos, 999999)
    data['distance_matrix'] = distance_matrix

    pickups_deliveries = []
    demands = [0] * num_nodes
    with open('requests.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = int(row['Pickup'])
            d = int(row['Delivery'])
            w = int(row['Demand'])
            pickups_deliveries.append([p, d])
            demands[p] = w
            demands[d] = -w
            
    data['pickups_deliveries'] = pickups_deliveries
    data['demands'] = demands
    data['depot'] = 0
    return data

def smooth_path(path_nodes, walls):
    """지그재그 궤적을 완전히 펴주는 범용 직각 알고리즘"""
    if not path_nodes or len(path_nodes) <= 2: return path_nodes
    
    def is_clear(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        for w in walls:
            if min_y == max_y: 
                y = min_y
                if w['y_min'] <= y <= w['y_max'] and not (max_x < w['x_min'] or min_x > w['x_max']):
                    return False
            elif min_x == max_x:
                x = min_x
                if w['x_min'] <= x <= w['x_max'] and not (max_y < w['y_min'] or min_y > w['y_max']):
                    return False
        return True

    def get_orthogonal_los(p1, p2):
        c1 = (p2[0], p1[1])
        if is_clear(p1, c1) and is_clear(c1, p2): return [p1, c1, p2]
        c2 = (p1[0], p2[1])
        if is_clear(p1, c2) and is_clear(c2, p2): return [p1, c2, p2]
        return None

    smoothed = [path_nodes[0]]
    curr_idx = 0
    while curr_idx < len(path_nodes) - 1:
        found_los = False
        for target_idx in range(len(path_nodes)-1, curr_idx, -1):
            los = get_orthogonal_los(path_nodes[curr_idx], path_nodes[target_idx])
            if los:
                if los[1] != los[0] and los[1] != los[2]:
                    smoothed.append(los[1])
                smoothed.append(los[2])
                curr_idx = target_idx
                found_los = True
                break
        if not found_los:
            curr_idx += 1
            smoothed.append(path_nodes[curr_idx])
            
    return smoothed

def interpolate_path(waypoints):
    if not waypoints: return []
    full_path = []
    for i in range(len(waypoints)-1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i+1]
        if x1 == x2:
            step = 1 if y2 > y1 else -1
            for y in range(y1, y2, step):
                full_path.append((x1, y))
        else:
            step = 1 if x2 > x1 else -1
            for x in range(x1, x2, step):
                full_path.append((x, y1))
    full_path.append(waypoints[-1])
    return full_path

def plot_routes(data, manager, routing, solution):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#1e1e1e')
    
    for w in data['walls']:
        width = w['x_max'] - w['x_min']
        height = w['y_max'] - w['y_min']
        rect = patches.Rectangle((w['x_min'], w['y_min']), width, height, linewidth=1, edgecolor='#222', facecolor='#444', alpha=0.9)
        ax.add_patch(rect)
    
    xs = [loc['x'] for loc in data['locations'][1:]]
    ys = [loc['y'] for loc in data['locations'][1:]]
    ax.scatter(xs, ys, c='gray', s=30, alpha=0.8, zorder=4) # 머신 포트 크기 강조
    
    depot_loc = data['locations'][data['depot']]
    ax.scatter(depot_loc['x'], depot_loc['y'], c='red', s=300, marker='*', zorder=5)
    
    colors = plt.cm.get_cmap('hsv', data['num_vehicles'])
    G = data['G']
    
    for vehicle_id in range(data['num_vehicles']):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            continue
            
        index = routing.Start(vehicle_id)
        route_nodes = []
        while not routing.IsEnd(index):
            route_nodes.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route_nodes.append(manager.IndexToNode(index))
        
        full_path_x, full_path_y = [], []
        for i in range(len(route_nodes) - 1):
            n1 = route_nodes[i]
            n2 = route_nodes[i+1]
            pos1 = (data['locations'][n1]['x'], data['locations'][n1]['y'])
            pos2 = (data['locations'][n2]['x'], data['locations'][n2]['y'])
            
            try:
                raw_path = nx.shortest_path(G, source=pos1, target=pos2)
                smooth_waypoints = smooth_path(raw_path, data['walls'])
                interp = interpolate_path(smooth_waypoints)
                for p in interp:
                    full_path_x.append(p[0])
                    full_path_y.append(p[1])
            except nx.NetworkXNoPath:
                pass
                
        c = colors(vehicle_id / max(1, data['num_vehicles'] - 1))
        ax.plot(full_path_x, full_path_y, linestyle='-', color=c, linewidth=3, alpha=0.8)
        
        key_x = [data['locations'][n]['x'] for n in route_nodes]
        key_y = [data['locations'][n]['y'] for n in route_nodes]
        ax.scatter(key_x, key_y, color=c, s=60, zorder=5, edgecolors='white', linewidths=1)
        
    ax.set_title("Factory Level AGV Routing Blueprint", color='white', fontsize=16)
    fig.patch.set_facecolor('#1e1e1e')
    ax.axis('off')
    return fig

def animate_routes(data, manager, routing, solution, filename="agv_ani.gif"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#1e1e1e') 
    
    for w in data['walls']:
        width = w['x_max'] - w['x_min']
        height = w['y_max'] - w['y_min']
        rect = patches.Rectangle((w['x_min'], w['y_min']), width, height, linewidth=1, edgecolor='#222', facecolor='#444', alpha=0.9)
        ax.add_patch(rect)
        
    xs = [loc['x'] for loc in data['locations'][1:]]
    ys = [loc['y'] for loc in data['locations'][1:]]
    ax.scatter(xs, ys, c='gray', s=30, alpha=0.8, zorder=4)
        
    depot_loc = data['locations'][data['depot']]
    ax.scatter(depot_loc['x'], depot_loc['y'], c='red', s=300, marker='*', zorder=5)
    
    colors = plt.cm.get_cmap('hsv', data['num_vehicles'])
    G = data['G']
    
    vehicle_paths = []
    max_frames = 0
    
    for vehicle_id in range(data['num_vehicles']):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            vehicle_paths.append({'x': [], 'y': []})
            continue
            
        index = routing.Start(vehicle_id)
        route_nodes = []
        while not routing.IsEnd(index):
            route_nodes.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route_nodes.append(manager.IndexToNode(index))
        
        full_path_x, full_path_y = [], []
        for i in range(len(route_nodes) - 1):
            n1 = route_nodes[i]
            n2 = route_nodes[i+1]
            pos1 = (data['locations'][n1]['x'], data['locations'][n1]['y'])
            pos2 = (data['locations'][n2]['x'], data['locations'][n2]['y'])
            
            try:
                raw_path = nx.shortest_path(G, source=pos1, target=pos2)
                smooth_waypoints = smooth_path(raw_path, data['walls'])
                interp = interpolate_path(smooth_waypoints)
                for idx, p in enumerate(interp):
                    if i > 0 and idx == 0: continue
                    full_path_x.append(p[0])
                    full_path_y.append(p[1])
            except nx.NetworkXNoPath:
                pass
        
        vehicle_paths.append({'x': full_path_x, 'y': full_path_y})
                
    def resolve_collisions(vehicle_paths):
        max_len = max([len(v['x']) for v in vehicle_paths]) if vehicle_paths else 0
        if max_len == 0: return vehicle_paths
        num_vehicles = len(vehicle_paths)
        active_vids = [vid for vid in range(num_vehicles) if len(vehicle_paths[vid]['x']) > 0]
        if not active_vids: return vehicle_paths
        
        resolved = {vid: {'x': [vehicle_paths[vid]['x'][0]], 'y': [vehicle_paths[vid]['y'][0]]} for vid in active_vids}
        ptrs = {vid: 1 for vid in active_vids}
        waits = {vid: 0 for vid in active_vids}
        
        step = 0
        while True:
            step += 1
            all_done = True
            proposed = {}
            for vid in active_vids:
                if ptrs[vid] < len(vehicle_paths[vid]['x']):
                    all_done = False
                    proposed[vid] = (vehicle_paths[vid]['x'][ptrs[vid]], vehicle_paths[vid]['y'][ptrs[vid]])
                else:
                    proposed[vid] = (resolved[vid]['x'][-1], resolved[vid]['y'][-1])
            if all_done: break
            
            approved = {}
            claimed_next = set()
            for vid in active_vids:
                if ptrs[vid] >= len(vehicle_paths[vid]['x']):
                    approved[vid] = proposed[vid]
                    claimed_next.add(proposed[vid])
                    
            for vid in active_vids:
                if vid in approved: continue
                curr = (resolved[vid]['x'][-1], resolved[vid]['y'][-1])
                nxt = proposed[vid]
                if nxt in claimed_next and waits[vid] < 10:
                    approved[vid] = curr
                    claimed_next.add(curr)
                    waits[vid] += 1
                else:
                    approved[vid] = nxt
                    claimed_next.add(nxt)
                    if nxt not in claimed_next or waits[vid] < 10:
                        waits[vid] = 0
                        ptrs[vid] += 1
                        
            for vid in active_vids:
                resolved[vid]['x'].append(approved[vid][0])
                resolved[vid]['y'].append(approved[vid][1])
            if step > max_len * 5: break
                
        new_paths = []
        for vid in range(num_vehicles):
            if vid in active_vids: new_paths.append(resolved[vid])
            else: new_paths.append({'x': [], 'y': []})
        return new_paths

    vehicle_paths = resolve_collisions(vehicle_paths)
    
    for v in vehicle_paths:
        if len(v['x']) > max_frames:
            max_frames = len(v['x'])
            
    for v in vehicle_paths:
        if len(v['x']) > 0 and len(v['x']) < max_frames:
            last_x = v['x'][-1]
            last_y = v['y'][-1]
            v['x'].extend([last_x] * (max_frames - len(v['x'])))
            v['y'].extend([last_y] * (max_frames - len(v['y'])))
            
    scatters = []
    for vehicle_id in range(data['num_vehicles']):
        if len(vehicle_paths[vehicle_id]['x']) > 0:
            c = colors(vehicle_id / max(1, data['num_vehicles'] - 1))
            
            # 1. 고정된 레일(전체 경로)을 배경에 연하게 미리 그려둡니다.
            ax.plot(vehicle_paths[vehicle_id]['x'], vehicle_paths[vehicle_id]['y'], 
                    color=c, linewidth=1.5, alpha=0.5, zorder=2)
            
            # 2. 이동하는 AGV 점 (trailing line은 삭제)
            scat = ax.scatter([], [], color=c, s=120, zorder=4, edgecolors='white', linewidths=1.5)
            scatters.append(scat)
        else:
            scatters.append(None)
            
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    ax.set_title("LIVE: Factory AGV Simulation", color='white', fontsize=18)
    fig.patch.set_facecolor('#1e1e1e')
    
    def update(frame):
        for vehicle_id in range(data['num_vehicles']):
            if scatters[vehicle_id] is not None:
                cur_x = vehicle_paths[vehicle_id]['x'][frame]
                cur_y = vehicle_paths[vehicle_id]['y'][frame]
                scatters[vehicle_id].set_offsets([[cur_x, cur_y]])
        return [s for s in scatters if s is not None]
        
    ani = FuncAnimation(fig, update, frames=max_frames, interval=50, blit=False)
    ani.save(filename, writer=PillowWriter(fps=30))
    plt.close(fig)
    return filename

def solve(time_limit=10, num_vehicles=10, mode="advanced"):
    data = create_data_model()
    data['num_vehicles'] = num_vehicles
    data['vehicle_capacities'] = [5] * num_vehicles
    
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    dimension_name = 'Distance'
    routing.AddDimension(transit_callback_index, 0, 999999, True, dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, data['vehicle_capacities'], True, 'Capacity'
    )

    penalty = 10000000 
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddDisjunction([pickup_index], penalty)
        routing.AddDisjunction([delivery_index], penalty)
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(routing.ActiveVar(pickup_index) == routing.ActiveVar(delivery_index))
        routing.solver().Add(routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
        routing.solver().Add(distance_dimension.CumulVar(pickup_index) <= distance_dimension.CumulVar(delivery_index))

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    
    if mode == "advanced":
        search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    else:
        search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC

    search_parameters.time_limit.seconds = time_limit
    search_parameters.log_search = False 

    start_time = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    end_time = time.time()

    return data, manager, routing, solution, end_time - start_time

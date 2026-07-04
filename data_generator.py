import csv
import random

def is_in_wall(x, y, walls):
    for w in walls:
        if w['x_min'] <= x <= w['x_max'] and w['y_min'] <= y <= w['y_max']:
            return True
    return False

def generate_data():
    random.seed(42)
    
    # 1. 복잡한 공정 라인 장벽(Walls) 생성
    walls = [
        {'id': 1, 'x_min': 10, 'x_max': 30, 'y_min': 10, 'y_max': 40}, # 좌측 하단 블록
        {'id': 2, 'x_min': 10, 'x_max': 30, 'y_min': 60, 'y_max': 90}, # 좌측 상단 블록
        {'id': 3, 'x_min': 40, 'x_max': 80, 'y_min': 10, 'y_max': 20}, # 우측 하단 블록
        {'id': 4, 'x_min': 40, 'x_max': 50, 'y_min': 40, 'y_max': 90}, # 중앙 세로 블록
        {'id': 5, 'x_min': 70, 'x_max': 90, 'y_min': 40, 'y_max': 90}, # 우측 상단 블록
    ]
    
    with open('walls.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'x_min', 'x_max', 'y_min', 'y_max'])
        writer.writeheader()
        writer.writerows(walls)
        
    # 2. 벽에 딱 붙은 30개의 도킹 스테이션(노드) 생성
    valid_ports = []
    for w in walls:
        # 벽의 4면 테두리(1칸 떨어져서)
        for x in range(w['x_min'], w['x_max'] + 1):
            valid_ports.append((x, w['y_min'] - 1))
            valid_ports.append((x, w['y_max'] + 1))
        for y in range(w['y_min'], w['y_max'] + 1):
            valid_ports.append((w['x_min'] - 1, y))
            valid_ports.append((w['x_max'] + 1, y))
            
    # 중복 및 맵 밖(0~100) 제거, 다른 벽과 겹치는지 체크
    clean_ports = []
    for p in set(valid_ports):
        x, y = p
        if 0 <= x <= 100 and 0 <= y <= 100:
            if not is_in_wall(x, y, walls):
                clean_ports.append(p)
                
    random.shuffle(clean_ports)
    selected_ports = clean_ports[:30] # 딱 30곳만 선정
    
    locations = []
    # 데포 위치 (중앙 출입구 쪽 여유 공간)
    locations.append({'node_id': 0, 'x': 50, 'y': 5})
    
    for i in range(1, 31):
        locations.append({'node_id': i, 'x': selected_ports[i-1][0], 'y': selected_ports[i-1][1]})
                
    with open('locations.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['node_id', 'x', 'y'])
        writer.writeheader()
        writer.writerows(locations)
        
    # 3. 픽업/배송 요청(Requests) 15쌍 생성
    pickups_deliveries = []
    available_nodes = list(range(1, 31))
    random.shuffle(available_nodes)
    
    for i in range(15):
        pickup = available_nodes.pop()
        delivery = available_nodes.pop()
        pickups_deliveries.append({
            'Pickup': pickup,
            'Delivery': delivery,
            'Demand': random.randint(1, 3) 
        })
        
    with open('requests.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Pickup', 'Delivery', 'Demand'])
        writer.writeheader()
        writer.writerows(pickups_deliveries)

    print("✅ 복합 공정 맵 생성 완료 (벽 부착형 30개 도킹 노드, 15쌍 배송 건)")

if __name__ == "__main__":
    generate_data()

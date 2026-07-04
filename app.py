import streamlit as st
import pandas as pd
from agv_routing import solve, plot_routes, animate_routes

st.set_page_config(page_title="Large-Scale AGV Control Simulator", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for High-End Look ---
st.markdown("""
<style>
    /* Force Dark Mode aesthetic */
    .reportview-container { background: #0e1117; }
    .sidebar .sidebar-content { background: #1a1c23; }
    h1 { color: #00e676; font-weight: 800; letter-spacing: -1px; }
    h3, h4 { color: #ffffff; }
    .stButton>button { 
        width: 100%; border-radius: 8px; font-weight: bold; 
        background-color: #00e676; color: black; border: none; 
        padding: 15px; font-size: 1.1rem;
    }
    .stButton>button:hover { background-color: #00c853; color: white; }
    div[data-testid="stMetric"] { 
        background-color: #1a1c23; padding: 20px; 
        border-radius: 12px; border: 1px solid #333; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Language selection
lang = st.sidebar.radio("🌐 Language / 언어", ["English", "한국어"])

# UI Strings Dictionary
ui = {
    "English": {
        "title": "🌐 Autonomous AGV Control Center",
        "desc": "Large-scale factory logistics routing simulator based on real field data (100 nodes). Experience the powerful dispatching performance of the Meta-heuristic AI algorithm.",
        "sidebar_header": "🕹️ Control Parameters",
        "mode_label": "🧠 Algorithm Tuning Level",
        "mode_options": ["Standard Mode", "Advanced AI Tuning"],
        "mode_help": "Advanced mode forces deep-dive search (GLS) to maximize dispatch optimization.",
        "time_limit": "⏱️ Computation Time Limit (sec)",
        "time_help": "Higher complexity requires more time to process all requests.",
        "num_vehicles": "🚛 Available AGVs",
        "render_anim": "🎥 Enable Animation Rendering",
        "render_help": "Generates an actual robot driving GIF. (Requires ~5-10 extra seconds)",
        "run_btn": "🚀 Start Simulation",
        "spinner_search": "AI Routing Engine is searching for trajectories... (Max {} sec)",
        "success": "✅ Optimal dispatching established! (Computation time: {:.2f}s)",
        "kpi_header": "### 📊 Real-time Dispatch Performance (KPIs)",
        "kpi_cost": "Optimization Cost Index",
        "kpi_active": "Active AGVs Dispatched",
        "kpi_standby": "{} on standby (Cost saved)",
        "kpi_dist": "Total Travel Distance",
        "blueprint": "#### 🗺️ Route Blueprint (Static)",
        "live": "#### 🎥 Large-scale Autonomous Simulation (LIVE)",
        "spinner_anim": "Processing traffic jams and rendering animation... (Please wait)",
        "error": "🚨 Unknown Error (Solver failed)",
        "info": "👈 Please adjust parameters in the left panel and click **[Start Simulation]**.",
        "db_status": "### 🏭 Current Factory Database Status",
        "nodes": "Work Locations (Nodes)",
        "requests": "Pending Logistics Requests",
        "walls": "Obstacle Structures (Walls)",
        "zones": "3 Zones"
    },
    "한국어": {
        "title": "🌐 자율주행 AGV 관제 센터",
        "desc": "실제 현장 데이터(100개 노드) 기반 초대규모 공장 물류 라우팅 시뮬레이터입니다. 메타휴리스틱 AI 알고리즘의 강력한 배차 최적화 성능을 경험해보세요.",
        "sidebar_header": "🕹️ 관제 파라미터 설정",
        "mode_label": "🧠 알고리즘 튜닝 레벨",
        "mode_options": ["일반 모드 (Standard)", "고성능 AI 튜닝 (Advanced)"],
        "mode_help": "고성능 모드는 딥 다이브 탐색(GLS)을 강제하여 배차를 극한까지 최적화합니다.",
        "time_limit": "⏱️ 최대 연산 허용 시간 (초)",
        "time_help": "복잡도가 높을수록 최적의 경로를 찾기 위해 더 많은 시간이 필요합니다.",
        "num_vehicles": "🚛 가용 AGV 대수",
        "render_anim": "🎥 라이브 애니메이션 렌더링 켜기",
        "render_help": "실제 로봇이 주행하는 GIF를 생성합니다. (약 5~10초 추가 소요)",
        "run_btn": "🚀 시뮬레이션 시작",
        "spinner_search": "AI 라우팅 엔진이 최적 궤적을 탐색 중입니다... (최대 {}초)",
        "success": "✅ 최적 배차 경로 수립 완료! (연산 소요 시간: {:.2f}초)",
        "kpi_header": "### 📊 실시간 배차 성과 지표 (KPI)",
        "kpi_cost": "최적화 비용 지수 (Cost)",
        "kpi_active": "현장 투입 AGV 대수",
        "kpi_standby": "{}대 유휴 대기 (비용 절감)",
        "kpi_dist": "총 이동 거리 합산",
        "blueprint": "#### 🗺️ 전체 경로 청사진 (Static)",
        "live": "#### 🎥 초대규모 자율주행 시뮬레이션 (LIVE)",
        "spinner_anim": "병목 현상 해결 및 주행 애니메이션 렌더링 중... (잠시만 기다려주세요)",
        "error": "🚨 알 수 없는 오류 (Solver 구동 실패)",
        "info": "👈 좌측 패널에서 파라미터를 설정한 뒤 **[시뮬레이션 시작]** 버튼을 눌러주세요.",
        "db_status": "### 🏭 현재 공장 데이터베이스 현황",
        "nodes": "작업 가능 거점 (노드)",
        "requests": "대기 중인 물류 요청",
        "walls": "장애물 구조물 (벽)",
        "zones": "3개 구역"
    }
}

t = ui[lang]

st.title(t["title"])
st.markdown(t["desc"])

# Sidebar settings
st.sidebar.header(t["sidebar_header"])
mode = st.sidebar.radio(t["mode_label"], t["mode_options"], help=t["mode_help"])
time_limit = st.sidebar.slider(t["time_limit"], 1, 60, 5, help=t["time_help"])
num_vehicles = st.sidebar.slider(t["num_vehicles"], 5, 30, 15, step=5)

st.sidebar.markdown("---")
render_anim = st.sidebar.checkbox(t["render_anim"], value=False, help=t["render_help"])

run_btn = st.sidebar.button(t["run_btn"])

# File data stats
locations_df = pd.read_csv("locations.csv")
requests_df = pd.read_csv("requests.csv")

if run_btn:
    selected_mode = "advanced" if "Advanced" in mode or "고성능" in mode else "default"
    
    with st.spinner(t["spinner_search"].format(time_limit)):
        data, manager, routing, solution, time_taken = solve(
            time_limit=time_limit,
            num_vehicles=num_vehicles,
            mode=selected_mode
        )
        
        if solution:
            st.success(t["success"].format(time_taken))
            
            # KPI calculation
            total_distance = 0
            used_vehicles = 0
            
            for vehicle_id in range(data['num_vehicles']):
                if routing.IsVehicleUsed(solution, vehicle_id):
                    used_vehicles += 1
                    index = routing.Start(vehicle_id)
                    while not routing.IsEnd(index):
                        previous_index = index
                        index = solution.Value(routing.NextVar(index))
                        total_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                        
            # KPI Metrics Board
            st.markdown(t["kpi_header"])
            col1, col2, col3 = st.columns(3)
            col1.metric(t["kpi_cost"], f"{solution.ObjectiveValue():,}")
            col2.metric(t["kpi_active"], f"{used_vehicles} / {num_vehicles}", delta=t["kpi_standby"].format(num_vehicles - used_vehicles), delta_color="normal")
            col3.metric(t["kpi_dist"], f"{total_distance:,} m")
            
            st.markdown("---")
            
            # Layout logic
            if render_anim:
                st.markdown(t["blueprint"])
                fig = plot_routes(data, manager, routing, solution)
                st.pyplot(fig)
                
                st.markdown("<br><hr><br>", unsafe_allow_html=True)
                
                st.markdown(t["live"])
                with st.spinner(t["spinner_anim"]):
                    gif_path = animate_routes(data, manager, routing, solution)
                    st.image(gif_path, use_container_width=True)
            else:
                st.markdown(t["blueprint"])
                fig = plot_routes(data, manager, routing, solution)
                st.pyplot(fig)
                
        else:
            st.error(t["error"])
else:
    st.info(t["info"])
    
    st.markdown(t["db_status"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t["nodes"], f"{len(locations_df)}")
    c2.metric(t["requests"], f"{len(requests_df)}")
    c3.metric(t["walls"], t["zones"])

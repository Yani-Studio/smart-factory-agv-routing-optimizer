<div align="center">

# 🏭 Smart Factory AGV Routing Optimizer

### _메타휴리스틱 AI 기반 대규모 공장 자율주행 물류 최적화 시뮬레이터_

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OR-Tools](https://img.shields.io/badge/Google_OR--Tools-VRP_Solver-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

**100개 노드 · 최대 50대 AGV · 실시간 충돌 회피(MAPF) · 웹 기반 관제 대시보드**

---

</div>

<br>

## 🎥 자율주행 시뮬레이션 (LIVE)

> 실제 공장 레이아웃 위에서 다수의 AGV가 물류 요청을 처리하며 자율 주행하는 모습입니다.  
> 각 로봇은 고유 색상으로 구분되며, 장애물(벽)을 피해 최적 경로를 따라 이동합니다.

<div align="center">

https://github.com/user-attachments/assets/5f83886b-e175-4764-a319-1dff4307cdb6

</div>

<br>

## 📊 성능 비교 분석

본 시뮬레이터는 **일반 모드(Standard)**와 **고성능 AI 튜닝 모드(Advanced)**를 제공합니다.  
동일한 물류 요청 데이터를 두 모드로 각각 처리한 뒤, 핵심 성과 지표(KPI)를 정량적으로 비교합니다.

### 🔀 일반 모드 vs 고성능 모드

| 지표 | 일반 모드 (Standard) | 고성능 모드 (Advanced) | 차이 |
|:---:|:---:|:---:|:---:|
| **알고리즘** | Greedy Descent | Guided Local Search (GLS) |  메타휴리스틱 탐색 |
| **최적화 비용(Cost)** | 2,309,776 | **2,309,452** | ✅ 비용 절감 |
| **작업 분배 편차** | 3.1 | **2.5** | ✅ 19% 균등화 |
| **연산 시간** | 2초 | 15초 | ⏱️ 정밀 탐색 소요 |

- **일반 모드**: 빠른 시간 내에 실행 가능한 경로를 생성합니다. 속도가 최우선인 운영 환경에 적합합니다.
- **고성능 모드**: GLS(Guided Local Search) 메타휴리스틱을 적용하여, 더 많은 연산 시간을 투자하는 대신 **비용 함수를 극한까지 최소화**하고 **AGV 간 작업량 편차를 대폭 줄여** 모든 로봇이 균등하게 일하도록 최적화합니다.

<br>

## 🧬 시스템 아키텍처

본 시스템은 **2단계 파이프라인(Two-Phase Pipeline)** 구조로 설계되었습니다.

<p align="center">
  <img src="visualization/architecture.png" width="100%" alt="High-Performance AGV Routing Architecture">
</p>

### Phase 1: 작업 배정 (Vehicle Routing Problem)
1. **물류 데이터 입력** — 노드 좌표, 물류 요청(픽업-배송 쌍), 장애물 정보
2. **OR-Tools 초기 해 생성** — 그리디(Greedy) 방식으로 실행 가능한 초기 경로 수립
3. **GLS 딥 서치 (고성능 모드)** — Guided Local Search 메타휴리스틱으로 비용 함수 최소화를 위한 반복 탐색
4. **배차 확정** — 제한 시간 내 발견된 최적 해를 최종 경로로 확정

### Phase 2: 시공간 충돌 회피 (MAPF)
1. **경로 배정** — Phase 1에서 확정된 각 AGV의 노드 방문 순서를 실제 그리드 경로로 변환
2. **병목 구간 탐지** — 다수의 AGV가 동일 구간을 동시에 통과하려는 충돌 상황 감지
3. **Time-Space A\* 우회 탐색** — 충돌 위험 발생 시, 시공간(Time-Space) 상에서 대기 또는 우회 경로 재탐색
4. **최종 주행 시뮬레이션** — 모든 충돌이 해소된 안전 경로로 실제 주행 애니메이션 생성

### 📈 연산 시간 & 최적화 비용 비교

<p align="center">
  <img src="visualization/lollipop_chart.png" width="90%" alt="연산 시간 및 최적화 비용 비교 (Lollipop Chart)">
</p>

> 고성능 모드는 15초간 딥 서치를 수행하여 일반 모드 대비 **더 낮은 비용 지수(Cost)**를 달성합니다.

### 🍩 경로 효율성 비교

<p align="center">
  <img src="visualization/donut_bar_charts.png" width="90%" alt="일반 모드 vs 고성능 모드 경로 효율성 (도넛 차트)">
</p>

> 두 모드 모두 단순 직선 거리 대비 **약 35%의 거리 절감(Consolidation)**을 달성하며, 고성능 모드가 근소하게 더 높은 효율을 보여줍니다.

### 📊 작업량 불균형 비교 (Task Count Standard Deviation)

<p align="center">
  <img src="visualization/donut_bar_charts_1.png" width="90%" alt="작업량 불균형 비교 (막대 차트)">
</p>

> 고성능 모드(Advanced)는 AGV 간 작업 건수 표준편차를 **3.1 → 2.5로 약 19% 개선**하여, 특정 로봇에 업무가 편중되는 현상을 효과적으로 완화합니다.

<br>

## 🖥️ 웹 기반 관제 대시보드

Streamlit 프레임워크로 구현된 실시간 웹 대시보드에서 파라미터 조절, 시뮬레이션 실행, KPI 확인, 경로 시각화까지 원스톱으로 수행할 수 있습니다.

<p align="center">
  <img src="visualization/sim_screen.png" width="100%" alt="AGV 관제 대시보드 스크린샷">
</p>

**주요 기능:**
- 🌐 **다국어 지원** — English / 한국어 실시간 전환
- 🧠 **알고리즘 모드 선택** — Standard / Advanced AI Tuning
- ⏱️ **연산 시간 조절** — 1초 ~ 60초 범위
- 🚛 **AGV 대수 설정** — 최대 50대 동시 투입
- 📍 **작업 노드 / 물류 요청 수 동적 생성** — 최대 100개 노드
- 💥 **MAPF 충돌 회피** — 데드락 타임아웃 설정 가능


## 🗺️ 경로 블루프린트 비교

실제 공장 레이아웃(장애물 포함) 위에 각 AGV의 최적 경로를 시각화한 결과입니다.

<table align="center">
  <tr>
    <td align="center"><b>🟢 일반 모드 (Standard)</b></td>
    <td align="center"><b>🟣 고성능 모드 (Advanced)</b></td>
  </tr>
  <tr>
    <td><img src="visualization/route_standard.png" width="100%" alt="일반 모드 라우팅 블루프린트"></td>
    <td><img src="visualization/route_advanced.png" width="100%" alt="고성능 모드 라우팅 블루프린트"></td>
  </tr>
  <tr>
    <td align="center"><i>빠른 연산, 실용적 경로</i></td>
    <td align="center"><i>심층 탐색, 극한 최적화 경로</i></td>
  </tr>
</table>

<br>

## 📂 프로젝트 구조

```
smart-factory-agv-routing-optimizer/
├── app.py                  # Streamlit 웹 대시보드 (메인 엔트리포인트)
├── agv_routing.py          # OR-Tools VRP 솔버 + MAPF 충돌 회피 + 시각화 엔진
├── data_generator.py       # 공장 데이터 자동 생성기 (노드, 요청, 벽)
└── visualization/          # 시각화 자료 모음
    ├── sim.mp4                 # 자율주행 시뮬레이션 영상
    ├── sim_screen.png          # 관제 대시보드 스크린샷
    ├── architecture.png        # 시스템 아키텍처 다이어그램
    ├── route_standard.png      # 일반 모드 경로 블루프린트
    ├── route_advanced.png      # 고성능 모드 경로 블루프린트
    ├── donut_bar_charts.png    # 경로 효율성 도넛 차트
    ├── donut_bar_charts_1.png  # 작업량 불균형 막대 차트
    ├── lollipop_chart.png      # 연산 시간 & 비용 롤리팝 차트
    └── agv_performance.ipynb   # 성능 분석 Jupyter Notebook
```

<br>

## 🚀 실행 방법

### 1. 환경 설치

```bash
pip install ortools streamlit pandas matplotlib numpy pillow
```

### 2. 시뮬레이터 실행

```bash
cd smart-factory-agv-routing-optimizer
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하면 관제 대시보드가 표시됩니다.

### 3. 성능 분석 노트북 실행

```bash
jupyter notebook visualization/agv_performance.ipynb
```

<br>

## 🛠️ 기술 스택

| 분류 | 기술 |
|:---:|:---|
| **최적화 엔진** | Google OR-Tools (CP-SAT / VRP Solver) |
| **메타휴리스틱** | Guided Local Search (GLS), Greedy Descent |
| **충돌 회피** | Multi-Agent Pathfinding (MAPF), Time-Space A* |
| **웹 프레임워크** | Streamlit |
| **시각화** | Matplotlib, Pillow (GIF Rendering) |
| **데이터 처리** | Pandas, NumPy |
| **언어** | Python 3.10+ |

<br>

## 📚 참고 문헌 및 데이터 출처

### 최적화 모델

| 참고 자료 | 설명 |
|:---|:---|
| [Google OR-Tools — Vehicle Routing Problem (VRP)](https://developers.google.com/optimization/routing) | 본 프로젝트의 핵심 솔버. Capacity Constraints, Pickup & Delivery, Time Windows 등 다양한 VRP 변형 문제를 지원하는 Google의 오픈소스 최적화 라이브러리입니다. |
| [Google OR-Tools — Guided Local Search (GLS)](https://developers.google.com/optimization/routing/routing_options#local_search_options) | 고성능 모드에서 사용하는 메타휴리스틱 전략. 지역 최적해(Local Optimum)에 갇히는 것을 방지하기 위해 페널티 기반의 탈출 메커니즘을 적용합니다. |
| [Multi-Agent Pathfinding (MAPF) — Overview](https://mapf.info/) | 다수의 에이전트가 동일 환경에서 충돌 없이 목적지에 도달하는 경로를 탐색하는 문제의 이론적 배경입니다. |
| [Stern, R. et al. — "Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks" (2019)](https://ojs.aaai.org/index.php/SOCS/article/view/18510) | MAPF 문제의 정의, 변형, 벤치마크를 체계적으로 정리한 학술 논문입니다. Phase 2 충돌 회피 로직의 이론적 기반입니다. |

### 데이터 생성

| 항목 | 설명 |
|:---|:---|
| **공장 레이아웃** | `data_generator.py`에 의해 프로시저럴(Procedural) 방식으로 자동 생성됩니다. 노드 좌표, 장애물(벽) 구조, 물류 요청(Pickup-Delivery 쌍) 모두 실행 시마다 랜덤 시드 기반으로 새롭게 생성되며, 실제 제조 현장의 통로-작업대 배치 패턴을 모사합니다. |
| **거리 행렬** | 각 노드 쌍 간의 맨해튼 거리(Manhattan Distance)를 장애물 회피 경로 기반으로 계산하여 `distance_matrix.csv`로 출력합니다. |
| **물류 요청** | 생성된 노드 중 무작위로 Pickup-Delivery 쌍을 선정합니다. 요청 수는 대시보드에서 실시간으로 조절 가능합니다. |

### 추가 참고 자료

- [Google OR-Tools GitHub Repository](https://github.com/google/or-tools) — OR-Tools 소스코드 및 예제
- [Streamlit Documentation](https://docs.streamlit.io/) — 웹 대시보드 프레임워크 공식 문서
- [A* Search Algorithm — Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm) — Phase 2 우회 경로 탐색에 사용된 A* 알고리즘의 이론적 배경

<br>

<div align="center">

---

**Made with 🤖 by Gyumin Kang**

*스마트 팩토리의 미래를 코드로 설계합니다.*

</div>

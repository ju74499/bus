import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path

# 1. 페이지 설정 및 DB 경로 확인
st.set_page_config(page_title="서울시 버스 분석 대시보드", layout="wide")

# DB 파일 경로 설정 (상대 경로 사용)
DB_PATH = Path(__file__).parent / "bus_dashboard_compact.db"

def get_connection():
    if not DB_PATH.exists():
        st.error(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {DB_PATH}")
        st.info("프로젝트 폴더 내에 'bus_dashboard_compact.db' 파일이 있는지 확인해주세요.")
        st.stop()
    return sqlite3.connect(DB_PATH)

# 2. 대시보드 제목 및 소개
st.title("🚌 서울시 버스 정류장별 승하차 패턴 및 공간 분포 분석")
st.markdown("""
이 대시보드는 서울시 버스 이용 데이터를 활용하여 **시간대별 이용량, 공간적 분포, 노선별 집중도**를 분석합니다. 
데이터는 SQLite DB에서 SQL 쿼리를 통해 직접 추출됩니다.
""")

# 3. 사이드바 필터 설정
conn = get_connection()

st.sidebar.header("📍 분석 필터")

# 필터를 위한 데이터 로드
try:
    bus_types = pd.read_sql("SELECT DISTINCT transport_type_name FROM hourly_bus_usage", conn)['transport_type_name'].tolist()
    selected_bus_type = st.sidebar.multiselect("버스 유형 선택", bus_types, default=bus_types)

    map_limit = st.sidebar.slider("지도에 표시할 정류장 수 (상위순)", 50, 1000, 300)
except:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.stop()

# --- 상단 주요 지표 (KPI) ---
st.divider()
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

# KPI용 SQL
total_users_sql = "SELECT SUM(total_users) FROM daily_bus_usage"
total_stops_sql = "SELECT COUNT(DISTINCT bus_stop_ars_id) FROM bus_station_info"
total_routes_sql = "SELECT COUNT(DISTINCT route_name) FROM daily_bus_usage"
top_stop_sql = "SELECT stop_name FROM daily_bus_usage GROUP BY bus_stop_ars_id ORDER BY SUM(total_users) DESC LIMIT 1"

with conn:
    total_users = pd.read_sql(total_users_sql, conn).iloc[0, 0]
    total_stops = pd.read_sql(total_stops_sql, conn).iloc[0, 0]
    total_routes = pd.read_sql(total_routes_sql, conn).iloc[0, 0]
    top_stop = pd.read_sql(top_stop_sql, conn).iloc[0, 0]

kpi_col1.metric("총 승하차 인원(4월)", f"{total_users:,.0f}명")
kpi_col2.metric("총 정류장 수", f"{total_stops:,.0f}개")
kpi_col3.metric("총 노선 수", f"{total_routes:,.0f}개")
kpi_col4.metric("최다 이용 정류장", top_stop)

# --- 차트 시각화 ---

# 1. 시간대별 전체 승하차 인원
st.subheader("1. 시간대별 전체 승하차 인원")
query1 = """
SELECT '00시' AS time_slot, SUM("00시승차총승객수" + "00시하차총승객수") AS users FROM hourly_bus_usage
UNION ALL SELECT '01시', SUM("01시승차총승객수" + "01시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '02시', SUM("02시승차총승객수" + "02시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '03시', SUM("03시승차총승객수" + "03시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '04시', SUM("04시승차총승객수" + "04시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '05시', SUM("05시승차총승객수" + "05시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '06시', SUM("06시승차총승객수" + "06시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '07시', SUM("07시승차총승객수" + "07시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '08시', SUM("08시승차총승객수" + "08시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '09시', SUM("09시승차총승객수" + "09시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '10시', SUM("10시승차총승객수" + "10시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '11시', SUM("11시승차총승객수" + "11시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '12시', SUM("12시승차총승객수" + "12시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '13시', SUM("13시승차총승객수" + "13시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '14시', SUM("14시승차총승객수" + "14시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '15시', SUM("15시승차총승객수" + "15시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '16시', SUM("16시승차총승객수" + "16시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '17시', SUM("17시승차총승객수" + "17시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '18시', SUM("18시승차총승객수" + "18시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '19시', SUM("19시승차총승객수" + "19시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '20시', SUM("20시승차총승객수" + "20시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '21시', SUM("21시승차총승객수" + "21시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '22시', SUM("22시승차총객수" + "22시하차총승객수") FROM hourly_bus_usage
UNION ALL SELECT '23시', SUM("23시승차총승객수" + "23시하차총승객수") FROM hourly_bus_usage;
"""
df1 = pd.read_sql(query1, conn)
fig1 = px.line(df1, x='time_slot', y='users', markers=True, labels={'time_slot':'시간대', 'users':'이용객 수'}, title="서울시 버스 시간대별 이용량")
st.plotly_chart(fig1, use_container_width=True)
st.code(query1, language='sql')
st.info("💡 인사이트: 출근 시간(08시)과 퇴근 시간(18시)에 이용량이 급격히 증가하는 전형적인 통근/통학 패턴을 보입니다.")

col_left, col_right = st.columns(2)

# 2. 정류장별 TOP 10
with col_left:
    st.subheader("2. 이용량 상위 10개 정류장")
    query2 = """
    SELECT stop_name, SUM(total_users) AS total_users
    FROM daily_bus_usage
    GROUP BY bus_stop_ars_id, stop_name
    ORDER BY total_users DESC LIMIT 10;
    """
    df2 = pd.read_sql(query2, conn)
    fig2 = px.bar(df2, x='total_users', y='stop_name', orientation='h', labels={'total_users':'이용객 수', 'stop_name':'정류장명'})
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)
    st.code(query2, language='sql')
    st.info("💡 이용량 상위 정류장은 주로 대형 지하철역 인근이나 주요 환승 거점입니다.")

# 3. 노선별 TOP 10
with col_right:
    st.subheader("3. 이용량 상위 10개 노선")
    query3 = """
    SELECT route_no, SUM(total_users) AS total_users
    FROM daily_bus_usage
    GROUP BY route_no
    ORDER BY total_users DESC LIMIT 10;
    """
    df3 = pd.read_sql(query3, conn)
    fig3 = px.bar(df3, x='total_users', y='route_no', orientation='h', color_discrete_sequence=['orange'], labels={'total_users':'이용객 수', 'route_no':'노선번호'})
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)
    st.code(query3, language='sql')
    st.info("💡 상위 노선은 서울의 동서 또는 남북을 가로지르는 간선 노선들이 주를 이룹니다.")

# 4. 버스 유형별 이용량
st.subheader("4. 버스 유형별 이용량 비중")
query4 = """
SELECT transport_type_name, SUM(total_users) AS total_users
FROM hourly_bus_usage
GROUP BY transport_type_name;
"""
df4 = pd.read_sql(query4, conn)
fig4 = px.pie(df4, values='total_users', names='transport_type_name', hole=0.4, title="버스 유형별 점유율")
st.plotly_chart(fig4, use_container_width=True)
st.code(query4, language='sql')
st.info("💡 간선버스와 지선버스가 전체 이용량의 대부분을 차지하며 서울 시내 교통의 핵심 역할을 수행하고 있음을 알 수 있습니다.")

# 5. 정류장 이용량 지도 시각화 (JOIN 활용)
st.subheader(f"5. 정류장 이용량 공간 분포 (상위 {map_limit}개)")
query5 = f"""
WITH stop_usage AS (
    SELECT bus_stop_ars_id, MIN(stop_name) AS stop_name, SUM(total_users) AS total_users
    FROM daily_bus_usage GROUP BY bus_stop_ars_id
),
stop_location AS (
    SELECT bus_stop_ars_id, AVG(longitude) AS longitude, AVG(latitude) AS latitude
    FROM bus_station_info WHERE longitude IS NOT NULL AND latitude IS NOT NULL
    GROUP BY bus_stop_ars_id
)
SELECT u.stop_name, u.total_users, l.longitude, l.latitude, u.bus_stop_ars_id
FROM stop_usage u
JOIN stop_location l ON u.bus_stop_ars_id = l.bus_stop_ars_id
ORDER BY u.total_users DESC LIMIT {map_limit};
"""
df5 = pd.read_sql(query5, conn)
fig5 = px.scatter_map(df5, lat="latitude", lon="longitude", size="total_users", color="total_users",
                        hover_name="stop_name", hover_data=["bus_stop_ars_id", "total_users"],
                        color_continuous_scale=px.colors.sequential.YlOrRd, 
                        size_max=15, zoom=10, map_style="open-street-map")
st.plotly_chart(fig5, use_container_width=True)
st.code(query5, language='sql')
st.info("💡 지도를 통해 강남, 홍대, 서울역 등 주요 상업 및 업무지구에 이용량이 집중되어 있음을 시각적으로 확인할 수 있습니다.")

# 6. 노선 수와 이용량 비교 (JOIN 활용)
st.subheader("6. 정류장별 노선 수와 이용량의 상관관계")
query6 = """
WITH stop_usage AS (
    SELECT bus_stop_ars_id, MIN(stop_name) AS stop_name, SUM(total_users) AS total_users
    FROM daily_bus_usage GROUP BY bus_stop_ars_id
),
route_count AS (
    SELECT bus_stop_ars_id, COUNT(DISTINCT route_name) AS route_count
    FROM bus_station_info GROUP BY bus_stop_ars_id
)
SELECT u.stop_name, u.total_users, r.route_count
FROM stop_usage u
JOIN route_count r ON u.bus_stop_ars_id = r.bus_stop_ars_id
WHERE u.total_users > 1000
ORDER BY u.total_users DESC LIMIT 500;
"""
df6 = pd.read_sql(query6, conn)
fig6 = px.scatter(df6, x='route_count', y='total_users', hover_name='stop_name', 
                 size='total_users', color='total_users', labels={'route_count':'통과 노선 수', 'total_users':'총 이용량'})
st.plotly_chart(fig6, use_container_width=True)
st.code(query6, language='sql')
st.info("💡 노선 수가 많을수록 대체로 이용량이 많으나, 노선 수가 적음에도 특정 목적지 수요로 인해 이용량이 매우 높은 정류장(이상치)도 존재합니다.")

conn.close()
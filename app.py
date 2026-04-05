import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import math

# Thiết lập giao diện trang
st.set_page_config(page_title="VietLogistics AI Route Demo", layout="wide")
st.title("🚚 Demo: Tối ưu tuyến đường xanh bằng AI - VietLogistics")
st.markdown("Mô phỏng giải thuật AI tối ưu hóa lộ trình giao hàng nhằm giảm tiêu hao nhiên liệu và khí thải carbon.")

# Tạo dữ liệu giả lập (Các điểm giao hàng quanh TP.HCM)
@st.cache_data
def generate_mock_data(num_points=10):
    # Tọa độ trung tâm kho (VD: Kho tại Bình Dương/Thủ Đức)
    base_lat, base_lon = 10.8500, 106.7500 
    points = [{'id': 0, 'lat': base_lat, 'lon': base_lon, 'type': 'Kho (Depot)'}]
    
    for i in range(1, num_points):
        points.append({
            'id': i,
            'lat': base_lat + np.random.uniform(-0.1, 0.1),
            'lon': base_lon + np.random.uniform(-0.1, 0.1),
            'type': 'Điểm giao'
        })
    return pd.DataFrame(points)

# Hàm tính khoảng cách (Euclidean cơ bản)
def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# Thuật toán mô phỏng (Nearest Neighbor) để tìm đường ngắn nhất
def optimize_route(df):
    unvisited = df.index.tolist()
    current_node = unvisited.pop(0) # Bắt đầu từ kho
    optimized_order = [current_node]
    
    while unvisited:
        nearest_node = min(unvisited, key=lambda x: calculate_distance(
            df.loc[current_node, 'lat'], df.loc[current_node, 'lon'],
            df.loc[x, 'lat'], df.loc[x, 'lon']
        ))
        optimized_order.append(nearest_node)
        unvisited.remove(nearest_node)
        current_node = nearest_node
        
    optimized_order.append(0) # Quay về kho
    return optimized_order

# UI Điều khiển bên trái
with st.sidebar:
    st.header("Cài đặt mô phỏng")
    num_deliveries = st.slider("Số điểm giao hàng", min_value=5, max_value=20, value=10)
    run_ai = st.button("Chạy AI Tối Ưu")

# Xử lý dữ liệu
df = generate_mock_data(num_deliveries)

if run_ai:
    route_indices = optimize_route(df)
    ordered_df = df.iloc[route_indices].reset_index(drop=True)
else:
    ordered_df = df # Đường đi hỗn loạn ban đầu

# Hiển thị Bản đồ
col1, col2 = st.columns([2, 1])

with col1:
    # Vẽ bản đồ
    m = folium.Map(location=[10.8500, 106.7500], zoom_start=11)
    
    # Đánh dấu các điểm
    for i, row in ordered_df.iterrows():
        color = 'red' if row['type'] == 'Kho (Depot)' else 'blue'
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"ID: {row['id']} - {row['type']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

    # Vẽ đường đi (Line)
    coordinates = [[row['lat'], row['lon']] for i, row in ordered_df.iterrows()]
    folium.PolyLine(coordinates, color="green" if run_ai else "gray", weight=2.5, opacity=0.8).add_to(m)

    st_folium(m, width=700, height=500)

with col2:
    st.subheader("Phân tích dữ liệu")
    if run_ai:
        st.success("Trạng thái: Đã tối ưu (Màu xanh)")
        st.metric("Ước tính tiết kiệm nhiên liệu", "15 - 20%")
        st.metric("Giảm phát thải CO2", "~45 kg/chuyến")
    else:
        st.warning("Trạng thái: Chưa tối ưu (Giao ngẫu nhiên)")
        
    st.write("Thứ tự giao hàng:")
    st.dataframe(ordered_df[['id', 'type']])

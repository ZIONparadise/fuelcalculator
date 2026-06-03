import streamlit as st
import requests

TANK_CAPACITY = 70.0
OPINET_URL = "https://www.opinet.co.kr/api/avgAllPrice.do"

st.title("만땅 주유비 계산기")

st.write("연료탱크 용량: 70L")

@st.cache_data(ttl=60 * 60 * 6)
def get_gasoline_price():
    certkey = st.secrets["OPINET_API_KEY"]

    params = {
        "out": "json",
        "certkey": certkey
    }

    response = requests.get(OPINET_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    oils = data["RESULT"]["OIL"]

    for oil in oils:
        if oil["PRODCD"] == "B027":
            return float(oil["PRICE"]), oil["TRADE_DT"], oil["DIFF"]

    raise ValueError("휘발유 가격 정보를 찾을 수 없습니다.")

try:
    auto_price, trade_date, diff = get_gasoline_price()
    st.success(f"자동 조회 유가: {auto_price:,.2f} 원/L")
    st.caption(f"기준일: {trade_date}, 전일 대비: {diff}")
except Exception:
    st.warning("자동 유가 조회에 실패했습니다. 수동으로 입력해 주세요.")
    auto_price = 2000.0

fuel_price = st.number_input(
    "리터당 휘발유 가격 (원/L)",
    min_value=0.0,
    value=float(auto_price),
    step=5.0
)

remaining_distance = st.number_input(
    "트립상 주행 가능 거리 (km)",
    min_value=0.0,
    value=250.0,
    step=10.0
)

fuel_efficiency = st.number_input(
    "평균 연비 (km/L)",
    min_value=0.1,
    value=10.0,
    step=0.1
)

current_fuel = remaining_distance / fuel_efficiency
needed_fuel = max(TANK_CAPACITY - current_fuel, 0)
estimated_cost = needed_fuel * fuel_price

st.subheader("계산 결과")
st.metric("현재 남은 연료량", f"{current_fuel:.1f} L")
st.metric("만땅까지 필요한 주유량", f"{needed_fuel:.1f} L")
st.metric("예상 주유 금액", f"{estimated_cost:,.0f} 원")

if current_fuel > TANK_CAPACITY:
    st.warning("계산된 잔여 연료가 70L를 초과합니다. 입력값을 확인해 주세요.")

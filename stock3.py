import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts
import json
import numpy as np

# --- 앱 기본 설정 ---
st.set_page_config(
    page_title="Meta Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- 공통 함수 ---

def apply_custom_styles(background_color, title_color):
    custom_css = f"""
    <style>
    .stApp {{ background-color: {background_color}; }}
    h1 {{ color: {title_color}; }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

@st.cache_data
def load_and_preprocess_data(path='C:/Users/Admin/workspace/Streamlit/data\Meta Platforms Stock Price History.csv'):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df = df.sort_values(by='Date')
    df['time'] = df['Date'].dt.strftime('%Y-%m-%d')
    if df['Vol.'].dtype == 'object':
        df['Vol.'] = df['Vol.'].str.replace('M', '', regex=False).astype(float) * 1_000_000
    if df['Change %'].dtype == 'object':
        df['Change %'] = df['Change %'].str.replace('%', '', regex=False).astype(float)
    # 숫자형 변환 시 오류를 무시하도록 'coerce' 옵션 사용
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    return df

# --- 앱 실행 로직 ---

apply_custom_styles(background_color="#1f2126", title_color="white")

try:
    df = load_and_preprocess_data()
except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다: Meta Platforms Stock Price History.csv")
    st.info("스크립트와 동일한 폴더에 파일이 있는지 확인해주세요.")
    st.stop()
except Exception as e:
    st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 사이드바 ---
st.sidebar.title('♾️ META')
start_date = st.sidebar.date_input("📆 시작 날짜", value=df['Date'].min(), min_value=df['Date'].min(), max_value=df['Date'].max())
end_date = st.sidebar.date_input("📆 종료 날짜", value=df['Date'].max(), min_value=df['Date'].min(), max_value=df['Date'].max())

start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date)
df_filtered = df[(df['Date'] >= start_datetime) & (df['Date'] <= end_datetime)].copy() # SettingWithCopyWarning 방지

# --- 메인 페이지 컨텐츠 ---

# 1. 데이터 테이블 및 요약 정보
st.markdown("<h1 style='color: white;'>Meta 주가 데이터 원본 📈</h1>", unsafe_allow_html=True)
df_display = df_filtered.copy()
df_display['Date'] = df_display['Date'].dt.strftime('%m/%d/%Y')
st.dataframe(df_display, use_container_width=True, hide_index=True)
st.header("", divider="gray")

highest_price = df_filtered['Price'].max()
lowest_price = df_filtered['Price'].min()
average_price = df_filtered['Price'].mean()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<p style="font-size: 1rem; color: rgba(255, 255, 255, 0.7);">선택 기간 최고 주가</p><h3 style="color: white;">${highest_price:,.2f}</h3>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<p style="font-size: 1rem; color: rgba(255, 255, 255, 0.7);">선택 기간 최저 주가</p><h3 style="color: white;">${lowest_price:,.2f}</h3>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<p style="font-size: 1rem; color: rgba(255, 255, 255, 0.7);">선택 기간 평균 주가</p><h3 style="color: white;">${average_price:,.2f}</h3>', unsafe_allow_html=True)

st.header("", divider="gray")

# --- ✨ 차트 선택 Selectbox에 옵션 추가 ---
st.markdown("<h1 style='color: white;'>보고 싶은 차트를 선택하세요!</h1>", unsafe_allow_html=True)
chart_options = ['기본 주가 및 거래량 차트', '기술적 분석 차트 (MACD)', '주가와 이동평균선 비교']
selected_chart = st.selectbox("", chart_options)

# --- 선택에 따른 차트 렌더링 ---
if selected_chart == '기본 주가 및 거래량 차트':
    st.markdown("<h1 style='color: white;'>Meta 주가 및 거래량 차트 📈</h1>", unsafe_allow_html=True)
    price_data = df_filtered[['time', 'Price']].rename(columns={'Price': 'value'}).to_dict('records')
    volume_data = []
    for _, row in df_filtered.iterrows():
        color = '#26a69a' if row['Change %'] >= 0 else '#ef5350'
        volume_data.append({'time': row['time'], 'value': row['Vol.'], 'color': color})

    priceVolumeChartOptions = {
        "height": 500, "layout": {"background": {"type": 'solid', "color": '#131722'}, "textColor": '#d1d4dc'},
        "grid": {"vertLines": {"color": 'rgba(42, 46, 57, 0)'}, "horzLines": {"color": 'rgba(42, 46, 57, 0.6)'}}
    }
    priceVolumeSeries = [
        {"type": 'Area', "data": price_data, "options": {"topColor": 'rgba(38,198,218, 0.56)', "bottomColor": 'rgba(38,198,218, 0.04)', "lineColor": 'rgba(38,198,218, 1)', "lineWidth": 2}},
        {"type": 'Histogram', "data": volume_data, "options": {"priceFormat": {"type": 'volume'}, "priceScaleId": ""}, "priceScale": {"scaleMargins": {"top": 0.7, "bottom": 0}}}
    ]
    renderLightweightCharts([{"chart": priceVolumeChartOptions, "series": priceVolumeSeries}], 'priceAndVolume')

elif selected_chart == '기술적 분석 차트 (MACD)':
    st.markdown("<h1 style='color: white;'>기술적 분석 차트 (MACD) 📈</h1>", unsafe_allow_html=True)
    df_chart = df_filtered.copy()
    df_chart = df_chart.rename(columns={'Date': 'datetime', 'Price': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Vol.': 'volume'})
    df_chart['time'] = df_chart['datetime'].dt.strftime('%Y-%m-%d')

    exp12 = df_chart['close'].ewm(span=12, adjust=False).mean()
    exp26 = df_chart['close'].ewm(span=26, adjust=False).mean()
    macd_line = exp12 - exp26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    df_chart['macd_hist'] = macd_line - signal_line
    # ... (MACD 차트 코드 생략, 이전과 동일)
    # (이하 MACD 데이터 준비 및 렌더링 코드는 이전과 동일합니다)
    COLOR_BULL = 'rgba(38,166,154,0.9)'; COLOR_BEAR = 'rgba(239,83,80,0.9)'
    df_chart['volume_color'] = np.where(df_chart['open'] > df_chart['close'], COLOR_BEAR, COLOR_BULL)
    df_chart['macd_hist_color'] = np.where(df_chart['macd_hist'] > 0, COLOR_BULL, COLOR_BEAR)
    candles = json.loads(df_chart.filter(['time', 'open', 'high', 'low', 'close']).to_json(orient="records"))
    volume_tech = json.loads(df_chart.filter(['time', 'volume', 'volume_color']).rename(columns={"volume": "value", "volume_color": "color"}).to_json(orient="records"))
    macd_line_data = json.loads(df_chart.filter(['time']).assign(value=macd_line).to_json(orient="records"))
    signal_line_data = json.loads(df_chart.filter(['time']).assign(value=signal_line).to_json(orient="records"))
    macd_hist_data = json.loads(df_chart.filter(['time', 'macd_hist_color']).assign(value=df_chart['macd_hist']).rename(columns={"macd_hist_color":"color"}).to_json(orient="records"))
    chartMultipaneOptions = [{"height": 400, "layout": {"background": {"type": "solid", "color": '#131722'}, "textColor": "#d1d4dc"},"grid": {"vertLines": {"color": "rgba(42, 46, 57, 0.5)"},"horzLines": {"color": "rgba(42, 46, 57, 0.5)"}},"timeScale": {"timeVisible": True, "secondsVisible": False, "borderColor": "rgba(197, 203, 206, 0.4)"},"priceScale": {"borderColor": "rgba(197, 203, 206, 0.4)"},"watermark": {"visible": True, "fontSize": 48, "horzAlign": 'center', "vertAlign": 'center',"color": 'rgba(255, 255, 255, 0.1)', "text": 'META Daily',}},{"height": 150, "layout": {"background": {"type": 'solid', "color": 'transparent'}, "textColor": '#d1d4dc'},"grid": {"vertLines": {"color": 'rgba(42, 46, 57, 0)'},"horzLines": {"color": 'rgba(42, 46, 57, 0.6)'}},"timeScale": {"visible": False},"watermark": {"visible": True, "fontSize": 24, "horzAlign": 'left', "vertAlign": 'top',"color": 'rgba(255, 255, 255, 0.2)', "text": 'Volume',}},{"height": 150, "layout": {"background": {"type": "solid", "color": '#131722'}, "textColor": "#d1d4dc"},"grid": {"vertLines": {"color": "rgba(42, 46, 57, 0.5)"},"horzLines": {"color": "rgba(42, 46, 57, 0.5)"}},"timeScale": {"visible": False},"watermark": {"visible": True, "fontSize": 24, "horzAlign": 'left', "vertAlign": 'top',"color": 'rgba(255, 255, 255, 0.2)', "text": 'MACD',}}]
    seriesCandlestickChart = [{"type": 'Candlestick', "data": candles, "options": {"upColor": COLOR_BULL, "downColor": COLOR_BEAR, "borderVisible": False, "wickUpColor": COLOR_BULL, "wickDownColor": COLOR_BEAR}}]
    seriesVolumeChart = [{"type": 'Histogram', "data": volume_tech, "options": {"priceFormat": {"type": 'volume'}, "priceScaleId": ""}, "priceScale": {"scaleMargins": {"top": 0.7, "bottom": 0}}}]
    seriesMACDchart = [{"type": 'Line', "data": macd_line_data, "options": {"color": '#2962FF', "lineWidth": 2}},{"type": 'Line', "data": signal_line_data, "options": {"color": '#FF6D00', "lineWidth": 2}},{"type": 'Histogram', "data": macd_hist_data, "options": {"lineWidth": 1}}]
    renderLightweightCharts([{"chart": chartMultipaneOptions[0], "series": seriesCandlestickChart},{"chart": chartMultipaneOptions[1], "series": seriesVolumeChart},{"chart": chartMultipaneOptions[2], "series": seriesMACDchart}], 'multipane')

# --- 새로운 'Overlaid' 차트 로직 추가 ---
elif selected_chart == '주가와 이동평균선 비교':
    st.markdown("<h1 style='color: white;'>주가와 20일 이동평균선 비교 📈</h1>", unsafe_allow_html=True)
    
    # 1. 데이터 준비: 20일 이동평균선 계산
    df_filtered['sma20'] = df_filtered['Price'].rolling(window=20).mean()
    df_chart_data = df_filtered.dropna() # 이동평균선 계산으로 생긴 NaN 값 제거

    price_series_data = df_chart_data[['time', 'Price']].rename(columns={'Price': 'value'}).to_dict('records')
    sma_series_data = df_chart_data[['time', 'sma20']].rename(columns={'sma20': 'value'}).to_dict('records')

    # 2. 동적 마커 생성: 기간 내 최고/최저점 찾기
    highest_point = df_chart_data.loc[df_chart_data['High'].idxmax()]
    lowest_point = df_chart_data.loc[df_chart_data['Low'].idxmin()]
    
    markers = [
        {
            "time": highest_point['time'],
            "position": 'aboveBar',
            "color": '#ef5350',
            "shape": 'arrowDown',
            "text": f"High: ${highest_point['High']:.2f}",
        },
        {
            "time": lowest_point['time'],
            "position": 'belowBar',
            "color": '#26a69a',
            "shape": 'arrowUp',
            "text": f"Low: ${lowest_point['Low']:.2f}",
        }
    ]

    # 3. 차트 옵션 및 시리즈 정의
    overlaidAreaSeriesOptions = {
        "height": 500,
        "rightPriceScale": {
            "scaleMargins": {"top": 0.1, "bottom": 0.1},
            "mode": 0, # 0-Normal (절대값), 2-Percentage (백분율)
            "borderColor": 'rgba(197, 203, 206, 0.4)',
        },
        "timeScale": {"borderColor": 'rgba(197, 203, 206, 0.4)'},
        "layout": {
            "background": {"type": 'solid', "color": '#131722'}, # 다른 차트와 통일
            "textColor": '#ffffff',
        },
        "grid": {
            "vertLines": {"color": 'rgba(197, 203, 206, 0.4)', "style": 1},
            "horzLines": {"color": 'rgba(197, 203, 206, 0.4)', "style": 1}
        }
    }

    seriesOverlaidChart = [
        {   # 20일 이동평균선 시리즈
            "type": 'Area',
            "data": sma_series_data,
            "options": {
                "topColor": 'rgba(255, 192, 0, 0.7)',
                "bottomColor": 'rgba(255, 192, 0, 0.3)',
                "lineColor": 'rgba(255, 192, 0, 1)',
                "lineWidth": 2,
            }
        },
        {   # 주가 시리즈
            "type": 'Area',
            "data": price_series_data,
            "options": {
                "topColor": 'rgba(67, 83, 254, 0.7)',
                "bottomColor": 'rgba(67, 83, 254, 0.3)',
                "lineColor": 'rgba(67, 83, 254, 1)',
                "lineWidth": 2,
            },
            "markers": markers 
        }
    ]

    # 4. 차트 렌더링
    renderLightweightCharts([
        {
            "chart": overlaidAreaSeriesOptions,
            "series": seriesOverlaidChart
        }
    ], 'overlaid_sma')
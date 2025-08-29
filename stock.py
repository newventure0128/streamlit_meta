import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

# --- 앱 기본 설정 (가장 먼저 실행되어야 합니다) ---
st.set_page_config(
    page_title="Meta Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- 공통 함수 ---

# 앱 전체의 배경색을 설정하는 함수
def apply_custom_styles(background_color, title_color):
    """
    Streamlit 앱에 배경색과 제목 색상을 적용하는 함수
    """
    custom_css = f"""
    <style>
    /* 앱 전체 배경색 설정 */
    .stApp {{
        background-color: {background_color};
    }}

    /* 제목(h1 태그) 색상 설정 */
    h1 {{
        color: {title_color};
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# 데이터를 로드하고 전처리하는 함수 (캐시 사용으로 성능 향상)
@st.cache_data
def load_and_preprocess_data(path='C:/Users/Admin/workspace/Streamlit/data/Meta Platforms Stock Price History.csv'):
    """
    CSV 파일을 로드하고 차트에 맞게 데이터를 전처리하는 함수
    """
    df = pd.read_csv(path)
    
    # 날짜 형식 변환 ('MM/DD/YYYY' 형식임을 명시)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df = df.sort_values(by='Date')
    df['time'] = df['Date'].dt.strftime('%Y-%m-%d')

    # 'Vol.'(거래량) 열의 'M'을 제거하고 숫자로 변환
    if df['Vol.'].dtype == 'object':
        df['Vol.'] = df['Vol.'].str.replace('M', '', regex=False).astype(float) * 1_000_000

    # 'Change %'(변동률) 열의 '%'를 제거하고 숫자로 변환
    if df['Change %'].dtype == 'object':
        df['Change %'] = df['Change %'].str.replace('%', '', regex=False).astype(float)
        
    return df

# --- 페이지 정의 ---

# 🎈 'Table' 페이지: 원본 데이터프레임을 표시합니다.
def main_page():
    st.markdown("<h1 style='color: white;'>Meta 주가 및 거래량 차트 📈</h1>", unsafe_allow_html=True)
    
    try:
        # 데이터 로드 (전처리된 데이터가 아닌 원본 CSV 로드)
        df_raw = pd.read_csv('C:/Users/Admin/workspace/Streamlit/data/Meta Platforms Stock Price History.csv')
        st.dataframe(df_raw, use_container_width=True)
    except FileNotFoundError:
        st.error("파일을 찾을 수 없습니다: Meta Platforms Stock Price History.csv")
        st.info("스크립트와 동일한 폴더에 파일이 있는지 확인해주세요.")

# ❄️ 'Charts' 페이지: 가격 및 거래량 차트를 표시합니다.
def page2():
    st.markdown("<h1 style='color: white;'>Meta 주가 및 거래량 차트 📈</h1>", unsafe_allow_html=True)

    try:
        df = load_and_preprocess_data()
    except FileNotFoundError:
        st.error("파일을 찾을 수 없습니다: Meta Platforms Stock Price History.csv")
        st.info("스크립트와 동일한 폴더에 파일이 있는지 확인해주세요.")
        return # 오류 발생 시 함수 실행 중단
    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        return

    # 1. 차트 데이터 형식으로 가공
    price_data = df[['time', 'Price']].rename(columns={'Price': 'value'}).to_dict('records')
    
    volume_data = []
    for _, row in df.iterrows():
        color = '#26a69a' if row['Change %'] >= 0 else '#ef5350' # 상승(초록), 하락(빨강)
        volume_data.append({
            'time': row['time'],
            'value': row['Vol.'],
            'color': color
        })

    # 2. 차트 옵션 및 시리즈 설정
    priceVolumeChartOptions = {
        "height": 500,
        "rightPriceScale": {"scaleMargins": {"top": 0.2, "bottom": 0.25}, "borderVisible": False},
        "overlayPriceScales": {"scaleMargins": {"top": 0.7, "bottom": 0}},
        "layout": {"background": {"type": 'solid', "color": '#131722'}, "textColor": '#d1d4dc'},
        "grid": {"vertLines": {"color": 'rgba(42, 46, 57, 0)'}, "horzLines": {"color": 'rgba(42, 46, 57, 0.6)'}}
    }

    priceVolumeSeries = [
        {
            "type": 'Area', "data": price_data,
            "options": {
                "topColor": 'rgba(38,198,218, 0.56)', "bottomColor": 'rgba(38,198,218, 0.04)',
                "lineColor": 'rgba(38,198,218, 1)', "lineWidth": 2,
            }
        },
        {
            "type": 'Histogram', "data": volume_data,
            "options": {"priceFormat": {"type": 'volume'}, "priceScaleId": ""},
            "priceScale": {"scaleMargins": {"top": 0.7, "bottom": 0}}
        }
    ]

    # 3. Streamlit에 차트 렌더링
    renderLightweightCharts([
        {"chart": priceVolumeChartOptions, "series": priceVolumeSeries}
    ], 'priceAndVolume')

# --- 앱 실행 로직 ---

# 배경색 설정
apply_custom_styles(background_color="#1f2126", title_color="white")

# 사이드바 메뉴 구성
st.sidebar.title('META')
page_names_to_funcs = {'데이터 테이블': main_page, '주가 차트': page2}
selected_page = st.sidebar.selectbox("페이지 선택", page_names_to_funcs.keys())

# 선택된 페이지 실행
page_names_to_funcs[selected_page]()
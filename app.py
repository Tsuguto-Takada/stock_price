import streamlit as st
import yfinance as yf

# --- Streamlit ページ設定 ---
st.set_page_config(
    page_title="Japanese Banking Sector Dashboard",
    page_icon="🇯🇵",
    layout="wide"
)

# --- Bloomberg風カスタムCSS ---
st.markdown("""
<style>
/* ... (基本CSS) ... */
[data-testid="stAppViewContainer"], body { background-color: #000000; color: #FFFFFF; }
html, body, [class*="st-"], [data-testid="stText"] { color: #FFFFFF; }
.main .block-container {padding-top: 1.5rem; padding-bottom: 2rem; padding-left: 1rem; padding-right: 1rem;}
h1 {font-size: clamp(1.6rem, 7vw, 2.2rem); font-weight: bold; color: #F8A31B; line-height: 1.2;}
h3 {font-size: clamp(1.1rem, 4vw, 1.25rem); font-weight: bold; color: #F8A31B; margin-bottom: -10px;}
.stMetricLabel {color: #A9A9A9; font-size: 1rem;}
.stMetricValue {font-size: clamp(1.8rem, 7vw, 2.2rem); font-weight: bold; color: #FFFFFF;}
.stMetricDelta {font-size: clamp(1rem, 4vw, 1.1rem); font-weight: bold;}
hr {border-top: 1px solid #333333;}
.stCaption {color: #A9A9A9; text-align: right;}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #333333;
    color: #FFFFFF;
}

/* ★★★ マルチセレクトのドロップダウンメニューのスタイルを強制 ★★★ */
/* ドロップダウン全体の背景 */
[data-baseweb="popover"] ul {
    background-color: #1c1c1e;
}
/* ドロップダウンの各選択肢の文字色 */
[data-baseweb="popover"] ul li {
    color: #FFFFFF !important;
}
/* マウスを乗せた時の選択肢の背景色 */
[data-baseweb="popover"] ul li:hover {
    background-color: #333333;
}
</style>
""", unsafe_allow_html=True)

# --- 対象となる銀行のデータ ---
COMPETITORS_ORDER = [
    "横浜FG", "千葉銀行", "しずおかFG", "ふくおかFG",
    "あおぞら銀行", "きらぼしFG", "りそなHD", "三井住友トラスト"
]
MEGA_BANKS_ORDER = ["三菱UFJ (MUFG)", "三井住友 (SMFG)", "みずほ (Mizuho)"]
ALL_BANKS_ORDER = COMPETITORS_ORDER + MEGA_BANKS_ORDER
BANK_TICKERS = {
    "横浜FG": "7186.T", "千葉銀行": "8331.T", "しずおかFG": "5831.T",
    "ふくおかFG": "8354.T", "あおぞら銀行": "8304.T", "きらぼしFG": "7173.T",
    "りそなHD": "8308.T", "三井住友トラスト": "8309.T", "三菱UFJ (MUFG)": "8306.T",
    "三井住友 (SMFG)": "8316.T", "みずほ (Mizuho)": "8411.T"
}

# --- データ取得・処理を行う関数 ---
@st.cache_data(ttl=600)
def get_stock_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="2d")
        info = ticker.info
        return (hist, info) if not hist.empty and info else (None, None)
    except Exception:
        return None, None

def format_market_cap(cap):
    if not isinstance(cap, (int, float)) or cap == 0: return "N/A"
    trillion = 1_000_000_000_000
    value_in_trillion = cap / trillion
    return f"{value_in_trillion:.2f} 兆円"

# --- アプリケーション本体 ---
st.markdown('<h1>Japanese Banking Sector<br>Dashboard</h1>', unsafe_allow_html=True)
st.markdown('---')

# --- 選択UI ---
if 'selected_banks' not in st.session_state:
    st.session_state.selected_banks = ["横浜FG"]

def set_selected_banks(bank_list):
    st.session_state.selected_banks = bank_list

cols = st.columns(5)
with cols[0]: st.button("横浜FG", on_click=set_selected_banks, args=(["横浜FG"],), use_container_width=True)
with cols[1]: st.button("メガバンク", on_click=set_selected_banks, args=(MEGA_BANKS_ORDER,), use_container_width=True)
with cols[2]: st.button("他競合", on_click=set_selected_banks, args=(COMPETITORS_ORDER,), use_container_width=True)
with cols[3]: st.button("すべて選択", on_click=set_selected_banks, args=(ALL_BANKS_ORDER,), use_container_width=True)
with cols[4]: st.button("クリア", on_ck=set_selected_banks, args=([],), use_container_width=True)

selected_banks = st.multiselect(
    '比較したい銀行を選択してください',
    options=ALL_BANKS_ORDER,
    key='selected_banks'
)
st.markdown('---')

# --- 比較表示エリア ---
if selected_banks:
    sorted_selected_banks = sorted(selected_banks, key=lambda x: ALL_BANKS_ORDER.index(x))
    
    for bank_name in sorted_selected_banks:
        with st.expander(f"🏛️ {bank_name}", expanded=True):
            ticker_symbol = BANK_TICKERS[bank_name]
            hist, info = get_stock_data(ticker_symbol)

            if not info:
                st.error("データ取得失敗")
                continue
            
            try:
                latest_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                price_change = latest_price - previous_close
                percent_change = (price_change / previous_close) * 100
                
                shares_outstanding = info.get('sharesOutstanding', 0)
                market_cap_jpy = latest_price * shares_outstanding if shares_outstanding else 0
                pbr = info.get('priceToBook')

                metric_cols = st.columns(3)
                with metric_cols[0]:
                    st.metric(label="📈 株価", value=f"{latest_price:,.0f} 円", delta=f"{price_change:.2f} ({percent_change:.2f}%)")
                with metric_cols[1]:
                    st.metric(label="🏦 時価総額", value=format_market_cap(market_cap_jpy))
                with metric_cols[2]:
                    st.metric(label="⚖️ PBR (実績)", value=f"{pbr:.2f} 倍" if pbr else "N/A")

            except IndexError:
                st.error("2日分のデータなし")
            except Exception:
                st.error("処理エラー")
else:
    st.info('上記から比較したい銀行を選択してください。')

st.markdown('<br>', unsafe_allow_html=True)
st.caption('データソース: Yahoo Finance')
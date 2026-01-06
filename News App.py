import streamlit as st
import feedparser
import requests
import ssl
from datetime import datetime

# --- 設定頁面 (必須放在第一行) ---
st.set_page_config(
    page_title="財經戰情室",
    page_icon="📈",
    layout="centered", # 手機版適合置中
    initial_sidebar_state="collapsed"
)

# --- 核心：新聞來源 ---
RSS_SOURCES = {
    "🌍 國際焦點": [
        "https://news.google.com/rss/headlines/section/topic/WORLD?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "https://www.rfi.fr/tw/%E5%9C%8B%E9%9A%9B/rss"
    ],
    "💰 國際財經": [
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", 
        "https://tw.stock.yahoo.com/rss?category=intl-market"
    ],
    "📈 台灣財經": [
        "https://tw.stock.yahoo.com/rss?category=tw-market",
        "https://money.udn.com/rssfeed/news/1001/5590"
    ],
    "🤖 AI 與科技": [
        "https://technews.tw/feed/",
        "https://www.bnext.com.tw/rss"
    ]
}

# --- 核心：抓取函式 (加入快取機制，避免太頻繁抓取) ---
@st.cache_data(ttl=300) # 設定 300秒(5分鐘) 內不重複抓取，加快速度
def fetch_news(url_list):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }
    
    for url in url_list:
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                feed = feedparser.parse(response.text)
                if len(feed.entries) > 0:
                    return feed
        except:
            continue
    return None

# --- 介面設計 ---
st.title("🌅 我的財經戰情室")
st.caption(f"最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# 1. 嵌入 TradingView (使用 HTML 組件)
st.components.v1.html("""
    <div class="tradingview-widget-container">
    <div class="tradingview-widget-container__widget"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {
    "symbols": [
        { "proName": "TWSE:TAIEX", "title": "台灣加權" },
        { "proName": "TWSE:2330", "title": "台積電" },
        { "proName": "FOREXCOM:NSXUSD", "title": "那斯達克" },
        { "proName": "FX_IDC:USDTWD", "title": "美元/台幣" },
        { "proName": "TVC:US10Y", "title": "美債10年" }
    ],
    "showSymbolLogo": true,
    "colorTheme": "light",
    "isTransparent": false,
    "displayMode": "regular",
    "locale": "zh_TW"
    }
    </script>
    </div>
""", height=50) # 設定高度

# 2. 顯示新聞
if st.button('🔄 點我手動刷新新聞'):
    st.cache_data.clear() # 清除快取，強制重抓

for category, urls in RSS_SOURCES.items():
    st.header(category)
    feed = fetch_news(urls)
    
    if feed:
        # 用 Expander (展開收合) 讓手機版面更乾淨
        with st.expander(f"查看 {len(feed.entries[:8])} 則新聞", expanded=True):
            for entry in feed.entries[:8]:
                title = entry.title
                link = entry.link
                published = getattr(entry, 'published', '')[:16]
                
                # 直接顯示超連結與標題
                st.markdown(f"**[{title}]({link})**")
                st.caption(f"🕒 {published}")
                st.divider() # 分隔線
    else:
        st.error("⚠️ 暫時無法取得此分類新聞")
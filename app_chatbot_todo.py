# ============================================================
# app_chatbot_todo.py - Thời gian đúng múi giờ Việt Nam (+07)
# ============================================================
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO
import plotly.express as px

try:
    from underthesea import sentiment, word_tokenize, text_normalize
    from underthesea.feature_engineering.stopwords import stopwords
except ImportError:
    sentiment = None
    word_tokenize = None
    text_normalize = None
    stopwords = lambda: set()

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="Chatbot Phân tích Phản hồi", page_icon="🤖", layout="wide")

EMOJI_MAP = {"positive": "😊", "negative": "😟", "neutral": "⚪"}
VI_LABEL = {"positive": "Tích cực", "negative": "Tiêu cực", "neutral": "Trung lập"}

# Múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# ============================================================
# CACHING
# ============================================================
@st.cache_resource
def get_sentiment_model():
    try:
        from underthesea import sentiment
        return sentiment
    except:
        return None

@st.cache_resource
def load_stopwords():
    try:
        return set(stopwords())
    except:
        return {"và", "là", "của", "có", "không", "được", "cho", "với", "trong"}

# ============================================================
# PHÂN TÍCH - THỜI GIAN VIỆT NAM
# ============================================================
def analyze_feedback(text: str) -> dict:
    if not text or len(text.strip()) < 3:
        now_vn = datetime.now(VN_TZ)
        return {
            "sentiment": "neutral", 
            "confidence": 0.4, 
            "tokens": [],
            "message": "Phản hồi quá ngắn", 
            "time": now_vn.strftime("%d-%m-%Y %H:%M:%S")
        }

    model = get_sentiment_model()
    if not model:
        now_vn = datetime.now(VN_TZ)
        return {
            "sentiment": "neutral", 
            "confidence": 0.0, 
            "tokens": [],
            "message": "Model chưa sẵn sàng", 
            "time": now_vn.strftime("%d-%m-%Y %H:%M:%S")
        }

    try:
        cleaned = text_normalize(text) if text_normalize else text
        sent = model(cleaned)

        tokens = word_tokenize(cleaned) if word_tokenize else cleaned.split()
        stop_words = load_stopwords()
        clean_tokens = [t.lower().replace(" ", "_") for t in tokens 
                        if t.lower() not in stop_words and len(t) > 1]

        confidence = 0.88 if any(w in cleaned.lower() for w in ["hay","tốt","thích","hài_lòng","xuất_sắc"]) else \
                     0.88 if any(w in cleaned.lower() for w in ["kém","tệ","khó","chán","thất_vọng"]) else 0.72

        now_vn = datetime.now(VN_TZ)

        return {
            "sentiment": sent,
            "confidence": round(confidence, 2),
            "tokens": clean_tokens[:15],
            "message": None,
            "time": now_vn.strftime("%d-%m-%Y %H:%M:%S")   # ← Thời gian Việt Nam
        }
    except:
        now_vn = datetime.now(VN_TZ)
        return {
            "sentiment": "neutral", 
            "confidence": 0.5, 
            "tokens": [],
            "message": "Lỗi phân tích", 
            "time": now_vn.strftime("%d-%m-%Y %H:%M:%S")
        }

# ============================================================
# MAIN APP
# ============================================================
st.title("🤖 Chatbot Phân tích Phản hồi Sinh viên")

if "history" not in st.session_state:
    st.session_state.history = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📤 Upload File")
    uploaded = st.file_uploader("CSV hoặc Excel", type=["csv", "xlsx"])
    if uploaded and st.button("Phân tích file"):
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            col = next((c for c in df.columns if any(k in str(c).lower() for k in ["phản hồi","feedback","text"])), df.columns[0])
            for txt in df[col].dropna().astype(str):
                if txt.strip():
                    res = analyze_feedback(txt.strip())
                    st.session_state.history.append({"feedback": txt.strip(), "result": res})
                    st.session_state.messages.append({"role": "user", "content": txt.strip()})
                    st.session_state.messages.append({"role": "assistant", "content": "Đã phân tích"})
            st.success("Phân tích file hoàn tất!")
        except Exception as e:
            st.error(f"Lỗi: {e}")

    if st.session_state.history and st.button("📥 Tải lịch sử CSV"):
        df_exp = pd.DataFrame([{
            "Thời gian": h["result"]["time"],
            "Phản hồi": h["feedback"],
            "Cảm xúc": VI_LABEL.get(h["result"]["sentiment"], "Trung lập"),
            "Độ tin cậy": f"{h['result']['confidence']:.0%}"
        } for h in st.session_state.history])
        output = BytesIO()
        df_exp.to_csv(output, index=False, encoding="utf-8-sig")
        st.download_button("Tải xuống", output.getvalue(), "phan_hoi.csv", "text/csv")

# ── CHATBOT ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ô nhập chat
if prompt := st.chat_input("Nhập phản hồi của sinh viên tại đây..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    for line in [l.strip() for l in prompt.splitlines() if l.strip()]:
        result = analyze_feedback(line)
        st.session_state.history.append({"feedback": line, "result": result})

        sent = result["sentiment"]
        emoji = EMOJI_MAP.get(sent, "⚪")
        label = VI_LABEL.get(sent, "Trung lập")
        
        analysis_text = f"""
**Cảm xúc:** {emoji} **{label}**

* Độ tin cậy: **{result['confidence']:.0%}**
* Ngôn ngữ: **VI**
* Từ khóa: **{', '.join(result['tokens'][:12]) if result['tokens'] else 'Không có'}**
* Thời gian: **{result['time']}**
"""
        if result.get("message"):
            analysis_text += f"\n*{result['message']}*"

        st.session_state.messages.append({"role": "assistant", "content": analysis_text})
        with st.chat_message("assistant"):
            st.markdown(analysis_text)

    st.rerun()

# ── THỐNG KÊ (Ở DƯỚI) ──
if st.session_state.history:
    st.divider()
    st.subheader("📊 Phân tích & Thống kê")

    sentiments = [h["result"]["sentiment"] for h in st.session_state.history]
    total = len(sentiments)
    pos = sentiments.count("positive")
    neg = sentiments.count("negative")
    neu = sentiments.count("neutral")
    avg_conf = sum(h["result"]["confidence"] for h in st.session_state.history) / total if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng phản hồi", total)
    col2.metric("Tỉ lệ tích cực", f"{(pos/total*100):.1f}%" if total else "0.0%")
    col3.metric("Tỉ lệ tiêu cực", f"{(neg/total*100):.1f}%" if total else "0.0%")
    col4.metric("Độ tin cậy TB", f"{avg_conf:.1f}%")

    st.subheader("Phân bố cảm xúc phản hồi")
    count_df = pd.DataFrame({
        "Cảm xúc": ["Tích cực", "Tiêu cực", "Trung lập"],
        "Số lượng": [pos, neg, neu]
    })
    fig = px.bar(count_df, x="Cảm xúc", y="Số lượng", color="Cảm xúc",
                 color_discrete_map={"Tích cực":"#00cc66", "Tiêu cực":"#ff4d4d", "Trung lập":"#888888"},
                 text="Số lượng")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Xu hướng cảm xúc theo thời gian")
    df_time = pd.DataFrame([{
        "time": h["result"]["time"],
        "score": 1 if h["result"]["sentiment"] == "positive" else -1 if h["result"]["sentiment"] == "negative" else 0
    } for h in st.session_state.history])
    df_time["time"] = pd.to_datetime(df_time["time"], format="%d-%m-%Y %H:%M:%S", errors='coerce')
    if not df_time.empty:
        fig2 = px.line(df_time, x="time", y="score", markers=True)
        st.plotly_chart(fig2, use_container_width=True)
import streamlit as st
import PyPDF2
import docx
import time
import pandas as pd
from io import BytesIO
from rouge_score import rouge_scorer # <-- [MỚI] Thư viện tính điểm học thuật
import plotly.express as px

# --- IMPORT CÁC MODULE XỬ LÝ ---
from summarizer_ai import TextSummarizer
from textrank_summarizer import TextRankSummarizer
from text_cleaner import TextPreprocessor
from groq_summarizer import GroqSummarizer
from cohere_summarizer import CohereSummarizer
import database 
import api_keys 

st.set_page_config(page_title="AI Summarizer Pro", page_icon="📝", layout="wide")
database.init_db()

@st.cache_resource
def load_models():
    return (
        TextSummarizer(), TextRankSummarizer(), TextPreprocessor(), 
        GroqSummarizer(api_keys.GROQ_KEY), CohereSummarizer(api_keys.COHERE_KEY)
    )

(ai_summarizer, textrank_summarizer, text_cleaner, groq_summarizer, cohere_summarizer) = load_models()

# ==========================================
# HÀM TÍNH TOÁN CÁC ĐỘ ĐO (METRICS)
# ==========================================
def calc_novelty(original_text, summary_text):
    """Tính tỷ lệ phần trăm từ vựng mới được AI tạo ra (Độ sáng tạo)"""
    orig_set = set(original_text.lower().split())
    summ_set = set(summary_text.lower().split())
    if not summ_set: return 0.0
    new_words = summ_set - orig_set
    return round((len(new_words) / len(summ_set)) * 100, 1)

def calc_rouge_l(reference_text, summary_text):
    """Tính điểm ROUGE-L (Mức độ hành văn giống với con người)"""
    if not reference_text.strip(): return 0.0
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)
    scores = scorer.score(reference_text, summary_text)
    return round(scores['rougeL'].fmeasure * 100, 1)

def extract_text_from_file(uploaded_file):
    try:
        filename = uploaded_file.name
        if filename.endswith('.txt'): return uploaded_file.getvalue().decode("utf-8")
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            return "".join([page.extract_text() + "\n" for page in pdf_reader.pages if page.extract_text()])
        elif filename.endswith('.docx'):
            doc = docx.Document(BytesIO(uploaded_file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
    return ""

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.title("📝 Hệ thống Tóm tắt & Nghiên cứu Đánh giá AI")
st.markdown("Đồ án chuyên sâu: Phân tích hiệu năng, đo lường độ sáng tạo (Novelty) và điểm chuẩn ROUGE giữa các thuật toán.")

st.sidebar.header("⚙️ Cấu hình chung")
summary_length = st.sidebar.slider("Độ dài tóm tắt mong muốn (số từ):", 30, 1000, 100)

st.subheader("📥 Dữ liệu đầu vào")
uploaded_file = st.file_uploader("📂 Tải lên tài liệu (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
input_content = extract_text_from_file(uploaded_file) if uploaded_file else ""

c_input, c_ref = st.columns(2)
with c_input:
    input_text = st.text_area("Nội dung văn bản cần xử lý (Bắt buộc):", value=input_content, height=200)
with c_ref:
    reference_text = st.text_area("Bản tóm tắt chuẩn của con người (Tùy chọn - Dùng để tính điểm ROUGE):", height=200, placeholder="Nhập bản tóm tắt mẫu vào đây để AI so sánh độ chính xác...")

cleaned_text = text_cleaner.clean_text(input_text)
original_word_count = len(cleaned_text.split())

tab1, tab2, tab3 = st.tabs(["📝 Tóm tắt Đơn", "⚖️ So sánh Đa mô hình", "📊 Dashboard & Lịch sử DB"])

# ---------------------------------------------------------
# TAB 1: TÓM TẮT ĐƠN
# ---------------------------------------------------------
with tab1:
    method = st.selectbox("Chọn mô hình AI:", [
        "Thông minh (AI T5 - Viết lại câu)", "Trích xuất ý chính (TextRank)",
        "⚡ Siêu tốc độ (Groq Llama 3 API)", "🌟 Tóm tắt chuyên sâu (Cohere API)"
    ])
    
    if st.button("🚀 Chạy Mô hình Đơn", type="primary"):
        if original_word_count < 20: st.warning("⚠️ Văn bản quá ngắn.")
        else:
            with st.spinner(f"🤖 Đang xử lý bằng {method}..."):
                start_time = time.time()
                try:
                    if "T5" in method: result = ai_summarizer.summarize(cleaned_text, max_len=summary_length)
                    elif "Groq" in method: result = groq_summarizer.summarize(cleaned_text, max_words=summary_length)
                    elif "Cohere" in method: result = cohere_summarizer.summarize(cleaned_text, max_words=summary_length)
                    else: result = textrank_summarizer.summarize(cleaned_text, num_sentences=max(1, summary_length // 20))
                    
                    p_time = round(time.time() - start_time, 2)
                    sum_count = len(result.split())
                    novelty = calc_novelty(cleaned_text, result)
                    rouge = calc_rouge_l(reference_text, result)
                    
                    st.success(result)
                    if not result.startswith("⚠️"):
                        database.save_summary(method, original_word_count, sum_count, p_time, cleaned_text, result, novelty, rouge)
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("⏱️ Thời gian", f"{p_time}s")
                    m2.metric("📉 Tỷ lệ nén", f"{round((sum_count/original_word_count)*100, 1)}%")
                    m3.metric("🧠 Độ sáng tạo (Novelty)", f"{novelty}%")
                    m4.metric("🎯 Điểm ROUGE-L", f"{rouge}%" if reference_text else "N/A")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# ---------------------------------------------------------
# TAB 2: SO SÁNH ĐA MÔ HÌNH
# ---------------------------------------------------------
with tab2:
    st.info("Chế độ này sẽ gửi văn bản đến 4 AI cùng lúc. Kèm theo chấm điểm Novelty (Tỷ lệ sinh từ mới) và ROUGE-L.")
    if st.button("⚖️ Bắt đầu Đại chiến AI (Chạy tất cả)", type="primary"):
        if original_word_count < 20: st.warning("⚠️ Văn bản quá ngắn.")
        else:
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            
            def render_result(col, title, res, time_taken, method_name):
                with col:
                    st.markdown(f"### {title}")
                    st.write(res)
                    if not res.startswith("⚠️"):
                        sum_cnt = len(res.split())
                        nov = calc_novelty(cleaned_text, res)
                        rg = calc_rouge_l(reference_text, res)
                        st.caption(f"⏱️ {time_taken}s | 📝 {sum_cnt} từ | 🧠 Novelty: {nov}% | 🎯 ROUGE: {rg if reference_text else 'N/A'}")
                        database.save_summary(method_name, original_word_count, sum_cnt, time_taken, cleaned_text, res, nov, rg)

            # 1. Llama 3 (Groq)
            start_t = time.time()
            res_groq = groq_summarizer.summarize(cleaned_text, max_words=summary_length)
            render_result(col1, "⚡ Groq (Llama 3)", res_groq, round(time.time() - start_t, 2), "⚡ Siêu tốc độ (Groq Llama 3 API)")
            
            # 2. Cohere
            start_t = time.time()
            res_co = cohere_summarizer.summarize(cleaned_text, max_words=summary_length)
            render_result(col2, "🌟 Cohere API", res_co, round(time.time() - start_t, 2), "🌟 Tóm tắt chuyên sâu (Cohere API)")
            
            # 3. T5 Local
            start_t = time.time()
            res_t5 = ai_summarizer.summarize(cleaned_text, max_len=summary_length)
            render_result(col3, "🧠 AI T5 (Offline)", res_t5, round(time.time() - start_t, 2), "Thông minh (AI T5 - Viết lại câu)")
                
            # 4. TextRank
            start_t = time.time()
            res_tr = textrank_summarizer.summarize(cleaned_text, num_sentences=max(1, summary_length // 20))
            render_result(col4, "✂️ TextRank", res_tr, round(time.time() - start_t, 2), "Trích xuất ý chính (TextRank)")

# ---------------------------------------------------------
# TAB 3: THỐNG KÊ & BIỂU ĐỒ
# ---------------------------------------------------------
with tab3:
    history_data = database.get_history()
    if len(history_data) == 0:
        st.write("Chưa có dữ liệu. Hãy chạy tóm tắt vài lần để xem biểu đồ!")
    else:
        df = pd.DataFrame(history_data, columns=["ID", "Thời gian", "Phương pháp", "Từ (Gốc)", "Từ (Tóm tắt)", "Thời gian xử lý (s)", "Văn bản gốc", "Kết quả", "Novelty (%)", "ROUGE-L (%)"])
        
        def shorten_name(name):
            if "T5" in name: return "AI T5 (Local)"
            if "TextRank" in name: return "TextRank"
            if "Groq" in name: return "Groq Llama 3"
            if "Cohere" in name: return "Cohere"
            return name
            
        df["Tên rút gọn"] = df["Phương pháp"].apply(shorten_name)
        df["Tỷ lệ nén (%)"] = (df["Từ (Tóm tắt)"] / df["Từ (Gốc)"]) * 100
        
        st.subheader("📈 Phân tích Các Chỉ Số Học Thuật")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**1. Tốc độ xử lý (giây)**")
            # THÊM CHÚ THÍCH GIẢI THÍCH BIỂU ĐỒ TỐC ĐỘ
            st.caption("⏳ Cột càng **THẤP** (thời gian ngắn) chứng tỏ AI chạy càng nhanh. Cột cao thể hiện độ trễ lớn, cần nhiều thời gian chờ đợi.")
            fig1 = px.bar(df.groupby("Tên rút gọn")["Thời gian xử lý (s)"].mean().reset_index(), x="Tên rút gọn", y="Thời gian xử lý (s)", text_auto='.2f', color="Tên rút gọn")
            fig1.update_layout(showlegend=False, xaxis_title="")
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            st.markdown("**2. Độ Sáng tạo - Novelty (%)**")
            # THÊM CHÚ THÍCH GIẢI THÍCH BIỂU ĐỒ NOVELTY
            st.caption("🧠 Cột càng **CAO** chứng tỏ AI có khả năng dùng từ vựng mới để viết lại câu (Paraphrase) càng tốt. TextRank luôn = 0 vì thuật toán này chỉ copy-paste câu gốc.")
            fig2 = px.bar(df.groupby("Tên rút gọn")["Novelty (%)"].mean().reset_index(), x="Tên rút gọn", y="Novelty (%)", text_auto='.1f', color="Tên rút gọn")
            fig2.update_layout(showlegend=False, xaxis_title="")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        c3, c4 = st.columns([2, 1])
        with c3:
            st.markdown("**3. Điểm Chuẩn ROUGE-L (%)**")
            # THÊM CHÚ THÍCH GIẢI THÍCH BIỂU ĐỒ ROUGE
            st.caption("🎯 Thanh càng **DÀI** (tỉ lệ cao) chứng tỏ cách hành văn của AI càng sát với bản tóm tắt chuẩn của con người. (Chỉ vẽ biểu đồ khi bạn có nhập Bản tóm tắt mẫu).")
            df_rouge = df[df["ROUGE-L (%)"] > 0]
            if not df_rouge.empty:
                fig3 = px.bar(df_rouge.groupby("Tên rút gọn")["ROUGE-L (%)"].mean().reset_index(), y="Tên rút gọn", x="ROUGE-L (%)", orientation='h', text_auto='.1f', color="Tên rút gọn")
                fig3.update_layout(showlegend=False, yaxis_title="")
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("💡 Bạn chưa nhập 'Bản tóm tắt chuẩn' lần nào nên chưa có biểu đồ ROUGE.")
                
        with c4:
            st.markdown("**4. Tỷ lệ nén văn bản (%)**")
            # THÊM CHÚ THÍCH GIẢI THÍCH TỶ LỆ NÉN
            st.caption("📦 Phần trăm số từ của bản tóm tắt so với bản gốc. Miếng bánh **NHỎ** nghĩa là AI tóm tắt siêu ngắn gọn. Miếng bánh **TO** là AI giữ lại nhiều chi tiết.")
            fig4 = px.pie(df.groupby("Tên rút gọn")["Tỷ lệ nén (%)"].mean().reset_index(), values="Tỷ lệ nén (%)", names="Tên rút gọn", hole=0.4)
            st.plotly_chart(fig4, use_container_width=True)
            
        st.markdown("---")
        st.subheader("📚 Bảng dữ liệu SQLite (Đã lưu điểm học thuật)")
        st.dataframe(df.drop(columns=["Văn bản gốc", "Kết quả", "Tên rút gọn", "Tỷ lệ nén (%)"], errors='ignore'), use_container_width=True)
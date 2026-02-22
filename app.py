import streamlit as st
import PyPDF2
import docx
from io import BytesIO
from summarizer_ai import TextSummarizer
from textrank_summarizer import TextRankSummarizer
from text_cleaner import TextPreprocessor

# ==========================================
# 1. CẤU HÌNH TRANG VÀ GIAO DIỆN
# ==========================================
st.set_page_config(page_title="AI Summarizer Pro", page_icon="📝", layout="wide")

# Hàm load model để lưu vào bộ nhớ cache (tránh load lại gây chậm)
@st.cache_resource
def load_models():
    return TextSummarizer(), TextRankSummarizer(), TextPreprocessor()

ai_summarizer, textrank_summarizer, text_cleaner = load_models()

# ==========================================
# 2. HÀM XỬ LÝ TRÍCH XUẤT VĂN BẢN
# ==========================================
def extract_text_from_file(uploaded_file):
    """Đọc nội dung từ file TXT, PDF hoặc DOCX"""
    try:
        filename = uploaded_file.name
        if filename.endswith('.txt'):
            return uploaded_file.getvalue().decode("utf-8")
        
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
            return text
        
        elif filename.endswith('.docx'):
            doc = docx.Document(BytesIO(uploaded_file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")
        return ""
    return ""

# ==========================================
# 3. GIAO DIỆN NGƯỜI DÙNG (UI)
# ==========================================
st.title("📝 Hệ thống Tóm tắt Văn bản Thông minh")
st.markdown("Hệ thống hỗ trợ tóm tắt đa định dạng, cho phép tùy chỉnh độ dài văn bản theo nhu cầu người đọc.")

# --- THANH ĐIỀU KHIỂN BÊN TRÁI (SIDEBAR) ---
st.sidebar.header("⚙️ Cấu hình tóm tắt")
summary_length = st.sidebar.slider("Độ dài tóm tắt mong muốn (số từ):", 30, 300, 100, help="AI sẽ cố gắng tóm tắt sát với số lượng từ này nhất.")
method = st.sidebar.selectbox(
    "Chọn phương thức tóm tắt:", 
    ["Thông minh (AI T5 - Viết lại câu)", "Trích xuất ý chính (TextRank - Giữ nguyên câu)"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Hướng dẫn:**
1. Tải file tài liệu hoặc dán văn bản.
2. Chọn độ dài và phương thức.
3. Nhấn nút 'Tiến hành Tóm tắt'.
""")

# --- KHU VỰC NHẬP DỮ LIỆU ---
st.subheader("📥 Dữ liệu đầu vào")
uploaded_file = st.file_uploader("📂 Tải lên tài liệu (Hỗ trợ: PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

# Xử lý tự động đổ dữ liệu từ file vào khung nhập liệu
input_content = ""
if uploaded_file is not None:
    with st.spinner("Đang trích xuất dữ liệu từ file..."):
        input_content = extract_text_from_file(uploaded_file)
        if input_content:
            st.success(f"✅ Đã nhận diện nội dung từ file: {uploaded_file.name}")

input_text = st.text_area(
    "Nội dung văn bản cần xử lý:", 
    value=input_content, 
    height=300, 
    placeholder="Nhập hoặc dán văn bản của bạn tại đây..."
)

# --- NÚT BẤM VÀ LOGIC XỬ LÝ ---
col1, col2 = st.columns([1, 4])
with col1:
    btn_run = st.button("🚀 Tiến hành Tóm tắt", type="primary")

if btn_run:
    if len(input_text.strip()) < 50:
        st.warning("⚠️ Văn bản quá ngắn (dưới 50 ký tự) để thực hiện tóm tắt chất lượng.")
    else:
        with st.spinner("🤖 AI đang đọc và phân tích văn bản..."):
            # 1. Làm sạch văn bản (Giữ lại dấu câu quan trọng)
            cleaned_text = text_cleaner.clean_text(input_text)
            
            # 2. Thực hiện tóm tắt theo phương thức đã chọn
            if method == "Thông minh (AI T5 - Viết lại câu)":
                result = ai_summarizer.summarize(cleaned_text, max_len=summary_length)
            else:
                # Tính toán số câu dựa trên số từ (Trung bình 20 từ/câu)
                num_sentences = max(1, summary_length // 20)
                result = textrank_summarizer.summarize(cleaned_text, num_sentences=num_sentences)
            
            # 3. Hiển thị kết quả
            st.markdown("---")
            st.subheader("📄 Kết quả tóm tắt:")
            st.success(result)
            
            # Thống kê nhanh
            word_count = len(result.split())
            st.info(f"📊 Độ dài bản tóm tắt: **{word_count} từ**.")

# Chân trang
st.markdown("---")
st.caption("Đồ án tốt nghiệp - Hệ thống tóm tắt văn bản tự động - 2024")
# 📝 Hệ thống Tóm tắt Văn bản Thông minh (AI Summarizer Pro)

**AI Summarizer Pro** là một ứng dụng web (Web App) hỗ trợ tóm tắt văn bản tự động dành riêng cho tiếng Việt. Hệ thống cho phép người dùng rút ngắn các tài liệu dài một cách nhanh chóng, chính xác trong khi vẫn giữ nguyên những ý chính cốt lõi, phục vụ hiệu quả cho việc học tập và nghiên cứu.

---

## 🚀 Chức năng chính

* **1. Hỗ trợ đa định dạng đầu vào:** Đọc và trích xuất nội dung tự động từ văn bản thuần túy hoặc các file tài liệu phổ biến như `PDF`, `DOCX` (Word), và `TXT`.
* **2. Hai chế độ tóm tắt linh hoạt:**
    * 🤖 **Tóm tắt thông minh (Abstractive Summarization):** Sử dụng mô hình Deep Learning (AI T5 của NlpHUST) để "đọc hiểu" và tự động viết lại đoạn văn ngắn gọn, logic, văn phong tự nhiên.
    * 📊 **Trích xuất ý chính (Extractive Summarization):** Sử dụng thuật toán TextRank và TF-IDF để chấm điểm và trích xuất giữ nguyên các câu mang thông tin quan trọng nhất của văn bản gốc.
* **3. Tùy chỉnh độ dài:** Người dùng có thể sử dụng thanh trượt (slider) để định hướng độ dài bản tóm tắt mong muốn (từ 30 đến 300 từ).
* **4. Trích xuất từ khóa (Keyword Extraction):** Tự động phân tích và hiển thị Top 5 từ khóa cốt lõi nhất của đoạn văn dưới dạng các thẻ (tags) trực quan.
* **5. Xuất và lưu trữ tài liệu:** Cung cấp tính năng tải xuống (Download) kết quả tóm tắt trực tiếp dưới định dạng `.txt` hoặc `.docx` với một cú click chuột.

---

## 🛠️ Công nghệ sử dụng

Dự án được xây dựng bằng ngôn ngữ **Python** và tích hợp các thư viện mạnh mẽ nhất hiện nay:
* **Giao diện Web:** `Streamlit` (Nhanh, trực quan, dễ sử dụng).
* **Xử lý ngôn ngữ tự nhiên (NLP) & AI:**
    * `Transformers` (HuggingFace) để chạy mô hình **T5-small-vi-summarization**.
    * `NLTK`, `Scikit-learn`, `NetworkX` để xây dựng thuật toán TextRank & TF-IDF.
* **Xử lý file tài liệu:** `PyPDF2` (đọc PDF), `python-docx` (đọc & xuất file Word).

---

## 📂 Cấu trúc dự án

* `app.py`: File chính chứa giao diện Streamlit và logic kết nối các thành phần.
* `config.py`: Lưu trữ các cấu hình chung (tên mô hình AI, giới hạn từ,...).
* `summarizer_ai.py`: Class xử lý tóm tắt bằng mô hình AI T5 (Abstractive).
* `textrank_summarizer.py`: Class xử lý tóm tắt và trích xuất từ khóa bằng TextRank (Extractive).
* `text_cleaner.py`: Class tiền xử lý, làm sạch văn bản đầu vào.
* `requirements.txt`: Danh sách các thư viện cần thiết để chạy dự án.

---

## 💻 Hướng dẫn Cài đặt & Sử dụng (Local)

Nếu bạn muốn chạy dự án này trên máy tính cá nhân, hãy làm theo các bước sau:

**Bước 1: Clone dự án về máy**
```bash
git clone [https://github.com/thinh220631/HeThongTomTatVanBan.git](https://github.com/thinh220631/HeThongTomTatVanBan.git)
cd HeThongTomTatVanBan
**Bước 2: Cài đặt các thư viện cần thiết**
```bash
pip install -r requirements.txt
**Bước 3: Khởi chạy ứng dụng**
```bash
streamlit run app.py
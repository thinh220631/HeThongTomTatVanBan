# 📝 Hệ thống Tóm tắt Văn bản Thông minh & Nghiên cứu Đánh giá AI (AI Summarizer Pro)

**AI Summarizer Pro** là một hệ thống phần mềm tóm tắt văn bản tiếng Việt đa mô hình. Dự án không chỉ dừng lại ở việc cung cấp công cụ tóm tắt, mà còn là một môi trường thực nghiệm để phân tích, so sánh hiệu năng và chất lượng giữa các thuật toán trích xuất truyền thống và các mô hình ngôn ngữ lớn (LLMs) tiên tiến nhất hiện nay.

---

## 🚀 Chức năng nổi bật

* **📂 Xử lý tài liệu đa định dạng:** Tự động đọc và trích xuất nội dung từ các tệp `PDF`, `DOCX` (Word) và `TXT`.
* **🧠 Hệ sinh thái đa mô hình AI:**
    * **TextRank:** Thuật toán trích xuất ý chính dựa trên đồ thị, giữ nguyên câu gốc.
    * **T5-Small (ViT5):** Mô hình Deep Learning tạo sinh được huấn luyện chuyên biệt cho tiếng Việt.
    * **Groq Llama 3:** Sử dụng API hiệu năng cao để tóm tắt bằng mô hình Llama 3 với tốc độ cực nhanh.
    * **Cohere API:** Tận dụng sức mạnh của mô hình ngôn ngữ thương mại để phân tích ngữ nghĩa sâu.
* **⚖️ Chế độ so sánh song song (Parallel Execution):** Tính năng cho phép chạy đồng thời tất cả các mô hình trên cùng một văn bản đầu vào để đối chiếu kết quả trực quan.
* **📊 Dashboard đánh giá học thuật:**
    * **Độ sáng tạo (Novelty Score):** Đo lường tỷ lệ từ vựng mới mà AI tự tạo ra so với bản gốc.
    * **Điểm ROUGE-L:** Đánh giá độ chính xác của bản tóm tắt dựa trên bản mẫu của con người.
    * **Phân tích hiệu năng:** Biểu đồ tương tác so sánh thời gian xử lý và tỷ lệ nén của từng phương pháp.
* **🗄️ Quản lý lịch sử bằng Database:** Tích hợp `SQLite` để lưu trữ mọi phiên làm việc, hỗ trợ tra cứu và thống kê dữ liệu thực nghiệm.

---

## 🛠️ Kiến trúc công nghệ

* **Giao diện:** `Streamlit` (Web Framework), `Plotly` (Biểu đồ tương tác).
* **Cơ sở dữ liệu:** `SQLite3` (Lưu trữ nội bộ).
* **Đánh giá học thuật:** `rouge-score` (Google Research metrics).
* **Xử lý ngôn ngữ:** `Transformers` (HuggingFace), `Groq SDK`, `Cohere SDK`, `NLTK`, `Scikit-learn`.

---

## 📂 Cấu trúc dự án

* `app.py`: Giao diện chính và luồng xử lý tập trung.
* `database.py`: Quản lý khởi tạo và truy vấn dữ liệu lịch sử.
* `summarizer_ai.py`: Xử lý mô hình T5 chạy cục bộ.
* `textrank_summarizer.py`: Xử lý thuật toán TextRank và trích xuất từ khóa.
* `groq_summarizer.py` & `cohere_summarizer.py`: Các module kết nối API đám mây.
* `text_cleaner.py`: Tiền xử lý và làm sạch dữ liệu văn bản.

---

## 💻 Hướng dẫn cài đặt

1.  **Clone dự án:**
    ```bash
    git clone [https://github.com/thinh220631/HeThongTomTatVanBan.git](https://github.com/thinh220631/HeThongTomTatVanBan.git)
    cd HeThongTomTatVanBan
    ```
2.  **Cài đặt thư viện:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Cấu hình API Key:**
    * Đổi tên file `api_keys.example.py` thành `api_keys.py`.
    * Điền các khóa API lấy từ Groq Cloud và Cohere Dashboard vào file.
4.  **Khởi chạy:**
    ```bash
    streamlit run app.py
    ```

---
**Đồ án 2 - Hệ thống tóm tắt văn bản thông minh tích hợp AI Cloud & Database.**
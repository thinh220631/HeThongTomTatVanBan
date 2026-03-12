import cohere

class CohereSummarizer:
    def __init__(self, api_key):
        # Sử dụng Client V2 để tương thích với hệ thống mới nhất 2026
        self.co = cohere.Client(api_key)

    def summarize(self, text, max_words=100):
        try:
            # Chuyển hẳn sang dùng Chat API vì Summarize API cũ không còn được hỗ trợ
            response = self.co.chat(
                model='command-r-plus-08-2024', # Dùng phiên bản ổn định nhất hiện nay
                message=f"Tóm tắt văn bản sau bằng tiếng Việt, khoảng {max_words} từ: {text}",
            )
            return response.text.strip()
        except Exception as e:
            # Trình bày lỗi gọn gàng cho đồ án
            return f"⚠️ Lỗi Cohere (New API): {str(e)}"
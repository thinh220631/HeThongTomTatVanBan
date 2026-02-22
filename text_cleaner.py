import re

class TextPreprocessor:
    def clean_text(self, text):
        if not text:
            return ""
            
        # 1. Xóa các khoảng trắng thừa, dấu xuống dòng, khoảng tab liên tiếp
        text = re.sub(r'\s+', ' ', text)
        
        # 2. Xóa các thẻ HTML (nếu lỡ copy từ web có dính code)
        text = re.sub(r'<[^>]+>', '', text)
        
        # LƯU Ý: Không dùng lệnh xóa ký tự đặc biệt chung chung ở đây nữa
        # Việc giữ lại các dấu câu (, . - / %) là bắt buộc để ngày tháng, tỉ số không bị dính vào nhau.
        
        return text.strip()
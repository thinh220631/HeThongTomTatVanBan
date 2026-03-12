from groq import Groq

class GroqSummarizer:
    def __init__(self, api_key):
        print("[HỆ THỐNG] Đang kết nối tới Groq Cloud API...")
        self.client = Groq(api_key=api_key)
        # Sử dụng model Llama 3 mới nhất, rất giỏi tiếng Việt
        self.model = "llama-3.3-70b-versatile" 

    def summarize(self, text, max_words=100):
        print(f"[HỆ THỐNG] Đang gửi dữ liệu lên Groq (Model: {self.model})...")
        
        prompt = f"""
        Bạn là một chuyên gia tóm tắt văn bản tiếng Việt.
        Nhiệm vụ: Tóm tắt văn bản dưới đây một cách súc tích, khoảng {max_words} từ.
        Yêu cầu: Giữ lại thông tin quan trọng nhất, hành văn tự nhiên.
        
        Văn bản cần tóm tắt:
        {text}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1024
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Lỗi Groq API: {str(e)}"
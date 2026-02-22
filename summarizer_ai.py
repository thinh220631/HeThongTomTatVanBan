from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import config
import torch

class TextSummarizer:
    def __init__(self):
        print("[HỆ THỐNG] Đang khởi tạo AI phiên bản Nâng cao (Chính xác ý)...")
        
        # Tải Tokenizer và Model
        print(" -> Đang tải Tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        
        print(" -> Đang tải Model (Hệ thống đang tối ưu hóa bộ nhớ)...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(config.MODEL_NAME)
        
        # Kiểm tra nếu có GPU (CUDA) thì chuyển model sang GPU để chạy nhanh và chính xác hơn
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        print(f"[HỆ THỐNG] Khởi tạo thành công trên thiết bị: {self.device.upper()}\n")

    def summarize(self, text, max_len=100):
        """
        Hàm tóm tắt nâng cấp: Đảm bảo thoát ý, không lặp, không cụt câu.
        """
        print(f"[HỆ THỐNG] Đang phân tích ngữ cảnh để tóm tắt (~{max_len} chữ)...")
        
        # KỸ THUẬT PROMPT MỚI: Dẫn dắt AI tập trung vào tóm tắt tiếng Việt chất lượng cao
        prompt_text = f"vietnamese summarization: {text}" 
        
        inputs = self.tokenizer(
            prompt_text, 
            max_length=1024, 
            return_tensors="pt", 
            truncation=True
        ).to(self.device) # Chuyển dữ liệu vào cùng thiết bị với model
        
        # THIẾT LẬP THAM SỐ SINH VĂN BẢN TỐI ƯU
        # Tăng biên độ để AI có không gian chọn từ ngữ hay nhất
        min_target = max(20, max_len - 30)
        max_target = max_len + 40 

        summary_ids = self.model.generate(
            inputs["input_ids"], 
            max_length=max_target, 
            min_length=min_target, 
            
            # CHIẾN THUẬT CHẤT LƯỢNG CAO
            num_beams=5,               # Tăng lên 5 để AI tìm con đường có nghĩa nhất
            length_penalty=1.2,        # Điều chỉnh để câu văn đủ ý, không quá ngắn
            no_repeat_ngram_size=3,    # Ngăn lặp lại cụm 3 chữ (giúp câu văn đa dạng)
            repetition_penalty=2.5,    # Phạt nặng việc lặp lại ý tứ cũ
            
            # Đảm bảo kết thúc chuyên nghiệp
            early_stopping=True,
            forced_eos_token_id=self.tokenizer.eos_token_id
        )
        
        # Giải mã
        summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        # HẬU XỬ LÝ (POST-PROCESSING): Xử lý lỗi cụt chữ cuối câu
        summary_text = summary_text.strip()
        
        # Nếu câu cuối cùng không có dấu kết thúc, ta tìm dấu chấm gần nhất hoặc thêm dấu ba chấm
        valid_endings = ('.', '!', '?', '\"', '”')
        if not summary_text.endswith(valid_endings):
            # Tìm vị trí dấu chấm cuối cùng để cắt bỏ phần chữ bị cụt phía sau
            last_dot = max(summary_text.rfind('.'), summary_text.rfind('!'), summary_text.rfind('?'))
            if last_dot != -1 and len(summary_text) - last_dot < 30: # Nếu đoạn cụt ngắn
                summary_text = summary_text[:last_dot + 1]
            else:
                summary_text += "..." # Nếu không tìm thấy dấu chấm, thêm dấu 3 chấm để báo hiệu còn ý

        return summary_text
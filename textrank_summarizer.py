import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx

class TextRankSummarizer:
    def __init__(self):
        print("[HỆ THỐNG] Đang tải mô hình TextRank...")
        # Tải bộ tách câu của NLTK (Đã cập nhật thêm punkt_tab cho phiên bản mới)
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt')
            nltk.download('punkt_tab')

    def summarize(self, text, num_sentences=2):
        print("[HỆ THỐNG] Đang tóm tắt bằng TextRank...")
        
        # 1. Tách đoạn văn thành các câu riêng biệt
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return text

        # ĐIỂM CỘNG ĐỒ ÁN: Khai báo danh sách Stop words tiếng Việt cơ bản
        vietnamese_stopwords = [
            "là", "và", "thì", "mà", "của", "các", "có", "để", "những", "một", 
            "trong", "với", "cho", "không", "này", "được", "về", "từ", "khi", 
            "đã", "đang", "sẽ", "như", "hay", "hoặc", "tại", "nó", "bởi", "ra", "vào"
        ]

        # 2. Dùng TF-IDF với tính năng loại bỏ Stop words
        vectorizer = TfidfVectorizer(stop_words=vietnamese_stopwords)
        X = vectorizer.fit_transform(sentences)
        
        # 3. Tính toán độ tương đồng (Similarity)
        similarity_matrix = (X * X.T).toarray()

        # 4. Xây dựng Đồ thị (Graph) và chạy PageRank
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)

        # 5. Xếp hạng câu và trích xuất
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        top_sentences = [s for score, s in ranked_sentences[:num_sentences]]
        
        return " ".join(top_sentences)

    def extract_keywords(self, text, num_keywords=5):
        """Trích xuất các từ khóa quan trọng nhất từ văn bản"""
        try:
            # Danh sách từ nối không mang ý nghĩa chính (Stopwords) mở rộng
            vietnamese_stopwords = [
                "là", "và", "thì", "mà", "của", "các", "có", "để", "những", "một", 
                "trong", "với", "cho", "không", "này", "được", "về", "từ", "khi", 
                "đã", "đang", "sẽ", "như", "hay", "hoặc", "tại", "nó", "bởi", "ra", "vào",
                "nhưng", "cũng", "việc", "đến", "ngày", "năm", "người", "theo", "sau"
            ]
            
            # Dùng TF-IDF để tìm các từ xuất hiện nhiều và có sức nặng
            vectorizer = TfidfVectorizer(stop_words=vietnamese_stopwords)
            X = vectorizer.fit_transform([text])
            
            # Lấy danh sách từ và điểm số
            words = vectorizer.get_feature_names_out()
            scores = X.toarray()[0]
            
            # Lọc ra Top 5 từ khóa điểm cao nhất
            top_indices = scores.argsort()[-num_keywords:][::-1]
            keywords = [words[i] for i in top_indices]
            
            return keywords
        except Exception as e:
            print(f"[LỖI] Trích xuất từ khóa thất bại: {e}")
            return []
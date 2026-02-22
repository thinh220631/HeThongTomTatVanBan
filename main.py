from summarizer_ai import TextSummarizer

def main():
    # 1. Khởi tạo bộ tóm tắt
    summarizer_system = TextSummarizer()

    # 2. Đầu vào văn bản
    sample_text = """
    Lập trình máy tính là quá trình thiết kế và xây dựng một chương trình máy tính có thể thực thi 
    để đạt được một kết quả tính toán cụ thể hoặc thực hiện một nhiệm vụ cụ thể. Việc lập trình 
    đòi hỏi các hoạt động như phân tích, tạo thuật toán, kiểm tra độ chính xác của thuật toán 
    và tiêu thụ tài nguyên, và triển khai thuật toán bằng một ngôn ngữ lập trình cụ thể. 
    Các ngôn ngữ lập trình phổ biến bao gồm Python, Java, C++, và JavaScript.
    """

    # 3. Yêu cầu AI tóm tắt
    summary_result = summarizer_system.summarize(sample_text)

    # 4. Hiển thị kết quả
    print("\n" + "="*40)
    print("KẾT QUẢ TÓM TẮT:")
    print("-" * 40)
    print(summary_result)
    print("="*40)

if __name__ == "__main__":
    main()
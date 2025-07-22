# A-Multi-Agent-System-For-Chart-Generation

**A-Multi-Agent-System-For-Chart-Generation** là hệ thống multi-agent tự động sinh truy vấn SQL, ánh xạ thực thể và vẽ biểu đồ từ yêu cầu tiếng Việt, sử dụng LLM (GPT-4o, Gemini) và Plotly. Dự án được thực hiện như là đồ án cuối khóa của chương trình thực tập sinh tài năng Viettel Digital Talent 2025 Phase I - DSAI Track

## Tính năng nổi bật

- **Sinh truy vấn SQL tự động:**  
  Chuyển đổi yêu cầu tiếng Việt thành truy vấn SQL phù hợp với dữ liệu thực tế.

- **Ánh xạ thực thể thông minh:**  
  Chuẩn hóa tên tỉnh/thành, dịch vụ... bằng kết hợp embedding ngữ nghĩa (PhoBERT/SBERT) và fuzzy matching, đảm bảo truy vấn chính xác dù người dùng nhập nhiều biến thể.

- **Sinh schema biểu đồ tự động:**  
  Phân tích yêu cầu, đề xuất loại biểu đồ phù hợp (bar, line, combo, pie...) và sinh schema JSON cho biểu đồ.

- **Vẽ biểu đồ tự động bằng Plotly:**  
  Sinh code Python vẽ biểu đồ từ schema và dữ liệu, hỗ trợ cả các trường hợp phức tạp như combo chart, multi-line, grouped bar.

## Luồng hoạt động

1. Nhận yêu cầu người dùng (tiếng Việt).
2. Agent sinh truy vấn SQL và schema biểu đồ bằng LLM.
3. Ánh xạ thực thể (tỉnh/thành, dịch vụ) về đúng giá trị trong dữ liệu.
4. Truy xuất dữ liệu bằng SQL.
5. Agent sinh và thực thi code vẽ biểu đồ tự động.

## Công nghệ sử dụng

- Python, Pandas, Plotly
- OpenAI GPT-4o, Gemini API
- SentenceTransformer (PhoBERT/SBERT)
- HuggingFace Transformers, PEFT, LoRA
- Fuzzy matching, Unidecode

## Cách sử dụng

1. Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```
2. Thêm API key vào `modules/secrets.toml`.
3. Chạy file chính:
    ```bash
    python main.py
    ```
4. Nhập yêu cầu phân tích dữ liệu bằng tiếng Việt, hệ thống sẽ tự động sinh SQL, ánh xạ thực thể và vẽ biểu đồ.

## Ví dụ yêu cầu

- Vẽ biểu đồ thực hiện lũy kế FTTx - TB thực tăng/giảm 5 tháng cuối năm 2024 của các thành phố Hà Nội, Đà Nẵng, Hồ Chí Minh
- Vẽ biểu đồ so sánh thực hiện DT dịch vụ nhóm DV của VTT năm 2024 của 3 tỉnh Quảng Bình, Quảng Trị, Thừa Thiên Huế
- Vẽ biểu đồ so sánh thực hiện lũy kế thuê bao 4g tăng thêm TP HCM 3 tháng cuối năm 2024 với cùng kỳ năm trước

## Đóng góp

Mọi đóng góp, phản hồi hoặc ý tưởng phát triển thêm đều được hoan nghênh!

---

**Ứng dụng:** Phân tích dữ liệu thống kê, báo cáo tự động, dashboard cho dữ liệu

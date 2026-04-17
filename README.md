# Chatbot Phân tích Phản hồi Sinh viên

Ứng dụng Streamlit này phân tích phản hồi của sinh viên theo cảm xúc (tích cực, tiêu cực, trung lập) và hiển thị kết quả cùng với thời gian theo múi giờ Việt Nam.

## Tính năng

- Giao diện chat tương tác để nhập phản hồi
- Tải lên file CSV hoặc Excel chứa phản hồi để phân tích hàng loạt
- Tự động xác định cột phản hồi từ tên cột chứa `phản hồi`, `feedback`, `text`
- Xuất lịch sử phản hồi dưới dạng file CSV
- Hiển thị biểu đồ và thống kê cảm xúc

## Yêu cầu

- Python 3.10+
- Streamlit
- pandas
- plotly
- pytz
- underthesea (tùy chọn, nếu không có vẫn chạy nhưng sẽ không phân tích đúng)

## Cài đặt

```bash
pip install streamlit pandas plotly pytz underthesea
```

## Chạy ứng dụng

```bash
streamlit run app_chatbot_todo.py
```

## Ghi chú

- Ứng dụng sử dụng múi giờ `Asia/Ho_Chi_Minh` để hiển thị thời gian Việt Nam.
- Nếu thiếu thư viện `underthesea`, ứng dụng vẫn cho phép chạy nhưng sẽ báo `Model chưa sẵn sàng` khi phân tích.

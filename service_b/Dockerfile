# Dockerfile cho service_b

FROM python:3.9-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép toàn bộ mã nguồn từ thư mục gốc vào thư mục /app trong container
COPY . .

# Cài đặt các phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Mở cổng cho gRPC
EXPOSE 50051

# Lệnh chạy server gRPC
CMD ["python", "server.py"]

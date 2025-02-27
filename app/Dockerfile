# Bước 1: Sử dụng Python base image
FROM python:3.9-slim

# Bước 2: Thiết lập thư mục làm việc trong container
WORKDIR /app

# Bước 3: Copy tệp requirements.txt vào container
COPY . .

# Bước 4: Cài đặt các phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Bước 5: Copy toàn bộ mã nguồn vào thư mục làm việc trong container
COPY . .

# Bước 6: Mở cổng mà ứng dụng sẽ chạy
EXPOSE 8188

# Bước 7: Lệnh chạy ứng dụng FastAPI với Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8188"]
FROM python:3.11-slim

WORKDIR /app

# uv 설치
RUN pip install uv

# 소스 코드 복사
COPY . .

# uv로 의존성 설치
RUN pip install -r requirements.txt

# 환경변수 설정
ENV PYTHONPATH=/app

# 서버 실행
CMD ["python", "main.py"]

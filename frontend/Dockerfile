FROM node:18-alpine

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm install --legacy-peer-deps

# 소스 코드 복사
COPY . .

# 환경 변수 설정
ENV NEXTAUTH_URL=http://localhost:3000

# 빌드
RUN npm run build

# 실행
CMD ["npm", "run", "start"]

EXPOSE 3000 
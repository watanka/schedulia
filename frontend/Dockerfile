FROM node:18-alpine

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm install --legacy-peer-deps

ENV PATH="/app/node_modules/.bin:$PATH"

# 소스 코드 복사
COPY . .

# 빌드
RUN npm run build

# 실행
CMD ["npm", "run", "start"]

EXPOSE 3000 

FROM nginx:alpine

# 기본 설정 파일 제거
RUN rm /etc/nginx/conf.d/default.conf


# 로그 디렉토리 생성
RUN mkdir -p /var/log/nginx

# 포트 80 노출
EXPOSE 80

# Nginx 디버그 모드로 실행
CMD ["nginx", "-g", "daemon off;"] 
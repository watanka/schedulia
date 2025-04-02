# 자체 서명 인증서 생성 스크립트 (개발 환경용)
$cert_path = "certbot/conf/live/schedulia.org"

# 필요한 디렉토리 생성
Write-Host "필요한 디렉토리 생성 중..."
if (-not (Test-Path $cert_path)) {
    New-Item -ItemType Directory -Path $cert_path -Force | Out-Null
}

# OpenSSL 확인
Write-Host "OpenSSL 확인 중..."
if (-not (Get-Command openssl -ErrorAction SilentlyContinue)) {
    Write-Host "OpenSSL이 설치되어 있지 않습니다."
    Write-Host "https://slproweb.com/products/Win32OpenSSL.html에서 설치 후 다시 시도하세요."
    exit 1
}

Write-Host "자체 서명 인증서 생성 중..."
# 인증서 생성
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$cert_path/privkey.pem" -out "$cert_path/fullchain.pem" -subj "/CN=schedulia.org" -addext "subjectAltName = DNS:schedulia.org,DNS:www.schedulia.org"

Write-Host "Nginx 컨테이너 재시작 중..."
docker-compose restart nginx

Write-Host "완료!"
Write-Host "주의: 이 인증서는 자체 서명된 것으로 브라우저에서 보안 경고가 표시됩니다." 
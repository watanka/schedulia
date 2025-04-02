# Let's Encrypt 초기화 PowerShell 스크립트
# 도메인 설정
$domains = @("schedulia.org", "www.schedulia.org")
$email = "admin@schedulia.org"
$staging = 1 # 테스트 시 1, 실제 발급 시 0
$data_path = "certbot"

# 필요한 디렉토리 생성
Write-Host "필요한 디렉토리 생성 중..."
if (-not (Test-Path $data_path)) {
    New-Item -ItemType Directory -Path $data_path | Out-Null
}
if (-not (Test-Path "$data_path/conf")) {
    New-Item -ItemType Directory -Path "$data_path/conf" | Out-Null
}
if (-not (Test-Path "$data_path/www")) {
    New-Item -ItemType Directory -Path "$data_path/www" | Out-Null
}

# 더미 인증서 생성 (첫 실행 시 필요)
$domains_args = $domains -join " -d "
$nginx_container = "nginx"

Write-Host "Nginx 컨테이너 시작 중..."
docker-compose up -d $nginx_container

# Let's Encrypt 인증서 발급
Write-Host "Let's Encrypt 인증서 발급 요청 중..."
$staging_arg = ""
if ($staging -eq 1) {
    $staging_arg = "--staging"
}

$certbot_command = "docker-compose run --rm certbot certonly $staging_arg --webroot --webroot-path=/var/www/certbot --email $email --agree-tos --no-eff-email --force-renewal -d $domains_args"
Write-Host "실행 명령어: $certbot_command"
Invoke-Expression $certbot_command

Write-Host "Nginx 설정 다시 불러오기..."
docker-compose exec $nginx_container nginx -s reload

Write-Host "완료!" 
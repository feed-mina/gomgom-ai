#!/bin/bash

echo " EC2 개발 환경 세팅 시작..."

# 시스템 패키지 업데이트
sudo apt update

# 필수 패키지 설치
sudo apt install -y python3-pip python3-venv default-mysql-client libmysqlclient-dev

# 가상환경 만들기
python3 -m venv venv
source venv/bin/activate

# Django 및 mysqlclient 설치
pip install django mysqlclient gunicorn

# 포트 열기
sudo ufw allow 8000

echo "🎉 Django + MySQL EC2 개발 환경 준비 완료!"

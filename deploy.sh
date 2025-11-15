#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== GCP 영어 스피킹 앱 배포 스크립트 ===${NC}\n"

# 프로젝트 ID 입력
read -p "GCP 프로젝트 ID를 입력하세요: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}프로젝트 ID가 필요합니다.${NC}"
    exit 1
fi

export PROJECT_ID

# 리전 설정
REGION="asia-northeast3"

echo -e "\n${GREEN}1. GCP 프로젝트 설정${NC}"
gcloud config set project ${PROJECT_ID}

echo -e "\n${GREEN}2. 필요한 API 활성화${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    speech.googleapis.com \
    texttospeech.googleapis.com

echo -e "\n${GREEN}3. Backend 이미지 빌드 및 배포${NC}"
cd backend

gcloud builds submit --tag gcr.io/${PROJECT_ID}/english-practice-backend

gcloud run deploy english-practice-backend \
  --image gcr.io/${PROJECT_ID}/english-practice-backend \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION} \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300

# Backend URL 가져오기
BACKEND_URL=$(gcloud run services describe english-practice-backend \
  --platform managed \
  --region ${REGION} \
  --format 'value(status.url)')

echo -e "\n${BLUE}Backend URL: ${BACKEND_URL}${NC}"

cd ..

echo -e "\n${GREEN}4. Frontend script.js 업데이트${NC}"
# API_BASE_URL 업데이트
sed -i "s|YOUR_BACKEND_CLOUD_RUN_URL|${BACKEND_URL}|g" frontend/script.js

echo -e "\n${GREEN}5. Frontend 이미지 빌드 및 배포${NC}"
cd frontend

gcloud builds submit --tag gcr.io/${PROJECT_ID}/english-practice-frontend

gcloud run deploy english-practice-frontend \
  --image gcr.io/${PROJECT_ID}/english-practice-frontend \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1

# Frontend URL 가져오기
FRONTEND_URL=$(gcloud run services describe english-practice-frontend \
  --platform managed \
  --region ${REGION} \
  --format 'value(status.url)')

echo -e "\n${GREEN}=== 배포 완료! ===${NC}"
echo -e "${BLUE}Frontend URL: ${FRONTEND_URL}${NC}"
echo -e "${BLUE}Backend URL: ${BACKEND_URL}${NC}"
echo -e "\n${GREEN}브라우저에서 ${FRONTEND_URL} 을 열어보세요!${NC}"

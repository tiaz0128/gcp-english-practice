# 배포 가이드

## 현재 진행 상황

Backend 이미지 빌드가 진행 중입니다.

## Backend 배포 완료 후

1. **Backend URL 확인**
```bash
gcloud run services describe english-practice-backend \
  --platform managed \
  --region asia-northeast3 \
  --format 'value(status.url)'
```

2. **Frontend script.js 업데이트**
`frontend/script.js` 파일에서 `YOUR_BACKEND_CLOUD_RUN_URL`을 실제 Backend URL로 변경

3. **Frontend 배포**
```bash
cd frontend
gcloud builds submit --tag gcr.io/gcp-english/english-practice-frontend

gcloud run deploy english-practice-frontend \
  --image gcr.io/gcp-english/english-practice-frontend \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated
```

## 서비스 테스트

Frontend URL로 접속하여 다음을 테스트:
1. 상황 입력 → 문장 생성
2. 마이크 버튼 클릭 → 발음
3. 피드백 확인

## 주의사항

- 현재 Vertex AI 연동은 예시 문장으로 대체됨
- Speech-to-Text는 정상 작동
- 추후 Vertex AI Gemini API 연동 추가 필요

# 배포 완료

## 서비스 URL

### 프론트엔드
https://english-practice-frontend-65867898884.asia-northeast3.run.app

### 백엔드
https://english-practice-backend-65867898884.asia-northeast3.run.app

## 사용 방법

1. 프론트엔드 URL에 접속합니다.
2. "상황 입력" 필드에 영어로 말하고 싶은 상황을 입력합니다 (예: cafe, restaurant, shopping, airport, hotel)
3. "문장 생성" 버튼을 클릭하여 추천 문장을 받습니다.
4. 추천 문장을 읽고 "녹음 시작" 버튼을 클릭합니다.
5. 마이크 권한을 허용하고 영어로 말합니다.
6. "녹음 중지" 버튼을 클릭하여 녹음을 종료합니다.
7. 발음 분석 결과와 피드백을 확인합니다.

## 아키텍처

- **프론트엔드**: nginx + HTML/CSS/JavaScript (Web Audio API)
- **백엔드**: Python FastAPI + Google Cloud Speech-to-Text
- **인프라**: Google Cloud Run (서버리스 컨테이너)
- **리전**: asia-northeast3 (서울)

## 주요 기능

1. **문장 생성**: 상황별 예제 문장 제공 (5가지 카테고리)
2. **음성 녹음**: Web Audio API를 통한 브라우저 녹음
3. **발음 분석**: Google Cloud Speech-to-Text API 활용
4. **피드백**: 정확도 점수 및 개선 제안

## 비용 최적화

- Cloud Run: 요청당 과금 (idle 시 비용 없음)
- Speech-to-Text: 월 60분 무료 (이후 분당 $0.006)
- 메모리: 백엔드 2Gi, 프론트엔드 기본값
- 타임아웃: 백엔드 300초

## 모니터링

Cloud Run 로그:
```bash
# 백엔드 로그
gcloud run logs read english-practice-backend --region asia-northeast3

# 프론트엔드 로그
gcloud run logs read english-practice-frontend --region asia-northeast3
```

## 재배포

백엔드 재배포:
```bash
cd /home/ubuntu/project/gcp-english/backend
gcloud builds submit --tag gcr.io/gcp-english/english-practice-backend
gcloud run deploy english-practice-backend --image gcr.io/gcp-english/english-practice-backend --region asia-northeast3
```

프론트엔드 재배포:
```bash
cd /home/ubuntu/project/gcp-english/frontend
gcloud builds submit --tag gcr.io/gcp-english/english-practice-frontend
gcloud run deploy english-practice-frontend --image gcr.io/gcp-english/english-practice-frontend --region asia-northeast3
```

# GCP 영어 스피킹 연습 앱

Google Cloud Platform의 Cloud Run, Vertex AI, Speech-to-Text를 활용한 영어 발음 연습 애플리케이션입니다.

## 주요 기능

1. **상황 기반 문장 생성**: Vertex AI(Gemini)를 사용하여 사용자가 입력한 상황에 맞는 영어 문장 생성
2. **음성 녹음**: 브라우저의 Web Audio API를 사용하여 사용자의 발음 녹음
3. **발음 분석**: Google Cloud Speech-to-Text로 음성 인식 후 AI 피드백 제공

## 기술 스택

### Backend
- Python 3.11
- FastAPI
- Google Cloud Vertex AI
- Google Cloud Speech-to-Text
- Docker

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Nginx

## 로컬 개발 환경 설정

### 사전 요구사항

1. Google Cloud Platform 프로젝트
2. GCP API 활성화:
   - Vertex AI API
   - Speech-to-Text API
   - Cloud Run API
3. 로컬에 GCP 인증 설정:
```bash
gcloud auth application-default login
```

### Backend 실행

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
export GCP_PROJECT_ID="your-project-id"
export GCP_LOCATION="us-central1"

# 서버 실행
python main.py
```

Backend는 http://localhost:8080 에서 실행됩니다.

### Frontend 실행

```bash
cd frontend

# 간단한 HTTP 서버 실행
python -m http.server 3000
```

Frontend는 http://localhost:3000 에서 실행됩니다.

`script.js`의 `API_BASE_URL`을 로컬 백엔드 주소로 설정하세요.

## Cloud Run 배포

### 1. Backend 배포

```bash
cd backend

# 프로젝트 ID 설정
export PROJECT_ID="your-project-id"

# Docker 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/${PROJECT_ID}/english-practice-backend

# Cloud Run 배포
gcloud run deploy english-practice-backend \
  --image gcr.io/${PROJECT_ID}/english-practice-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=us-central1
```

배포 후 제공되는 URL을 기록해두세요.

### 2. Frontend 배포

```bash
cd frontend

# script.js에서 API_BASE_URL을 백엔드 Cloud Run URL로 업데이트
# 예: const API_BASE_URL = 'https://english-practice-backend-xxx.run.app';

# Docker 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/${PROJECT_ID}/english-practice-frontend

# Cloud Run 배포
gcloud run deploy english-practice-frontend \
  --image gcr.io/${PROJECT_ID}/english-practice-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 환경 변수

### Backend
- `GCP_PROJECT_ID`: GCP 프로젝트 ID (필수)
- `GCP_LOCATION`: Vertex AI 리전 (기본값: us-central1)
- `PORT`: 서버 포트 (기본값: 8080)

## API 엔드포인트

### POST /api/generate-sentence
상황을 입력받아 적절한 영어 문장을 생성합니다.

**Request:**
```json
{
  "situation": "카페에서 커피 주문하기"
}
```

**Response:**
```json
{
  "sentence": "I'd like a medium iced coffee with oat milk, please.",
  "situation": "카페에서 커피 주문하기"
}
```

### POST /api/analyze-pronunciation
사용자의 음성을 분석하고 피드백을 제공합니다.

**Request:**
- Form Data
  - audio: 오디오 파일 (webm)
  - original_sentence: 원본 문장

**Response:**
```json
{
  "transcript": "I'd like a medium iced coffee with oat milk please",
  "original_sentence": "I'd like a medium iced coffee with oat milk, please.",
  "feedback": "전반적으로 발음이 정확합니다...",
  "pronunciation_score": 92.5
}
```

## 비용 최적화

- Cloud Run은 요청이 없을 때 자동으로 스케일 다운됩니다
- Vertex AI와 Speech-to-Text는 사용량 기반 과금입니다
- 개발 환경에서는 최소 인스턴스를 0으로 설정하는 것을 권장합니다

## 라이선스

MIT License

## 기여

이슈와 PR을 환영합니다!

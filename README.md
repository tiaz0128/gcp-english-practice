# GCP 영어 스피킹 연습 앱

Google Cloud Platform의 Cloud Run, Vertex AI, Speech-to-Text를 활용한 영어 발음 연습 애플리케이션입니다.

## 프로젝트 개요

- FOSS for all 컨퍼런스 자원봉사 다녀옴
- 외국인 참가자가 많았는데
- 영어로 말을 못하겠음..
- 영어 공부가 필요...
  - 앱은 비싸고
  - 만들기 고고

## 프로젝트 링크

<div align="center">
  <h3><a href="https://english-practice-frontend-okojbejsya-du.a.run.app/">URL 링크 클릭</h3>
  <img src="docs/url-qr.png" width="320px"/>
</div>

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

## 배포

```bash
$ ./deploy.sh
```



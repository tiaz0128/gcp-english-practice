from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from google.cloud import aiplatform
from google.cloud import speech_v1p1beta1 as speech
import os
import tempfile
import json

app = FastAPI(title="English Speaking Practice API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수
PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GCP_LOCATION", "asia-northeast3")


class SituationRequest(BaseModel):
    situation: str


class SentenceResponse(BaseModel):
    sentence: str
    situation: str


class FeedbackResponse(BaseModel):
    transcript: str
    original_sentence: str
    feedback: str
    pronunciation_score: float


@app.get("/")
async def root():
    return {"message": "English Speaking Practice API", "status": "running"}


@app.post("/api/generate-sentence", response_model=SentenceResponse)
async def generate_sentence(request: SituationRequest):
    """
    상황을 입력받아 적절한 영어 문장을 생성합니다.
    """
    if not PROJECT_ID:
        raise HTTPException(status_code=500, detail="GCP_PROJECT_ID가 설정되지 않았습니다")
    
    try:
        # Vertex AI 초기화
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # 프롬프트 생성
        prompt = f"""다음 상황에서 영어 초급자가 연습할 수 있는 간단하고 실용적인 영어 문장을 하나만 생성해주세요.

상황: {request.situation}

요구사항:
- 한 문장으로 작성
- 일상적이고 자연스러운 표현
- 초급~중급 수준의 난이도
- 실제로 사용할 수 있는 실용적인 문장

문장만 출력하세요 (설명이나 번역 없이):"""

        # Vertex AI Gemini 모델 사용
        model = GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # 생성된 문장 추출
        sentence = response.text.strip()
        
        # 불필요한 따옴표나 마침표 정리
        sentence = sentence.strip('"\'')
        if not sentence.endswith(('.', '!', '?')):
            sentence += '.'
        
        return SentenceResponse(
            sentence=sentence,
            situation=request.situation
        )
        
    except Exception as e:
        print(f"Vertex AI 오류: {str(e)}")
        # 폴백: 상황별 예시 문장
        example_sentences = {
            "카페": "I'd like a medium iced coffee with oat milk, please.",
            "식당": "Could I have the menu, please?",
            "쇼핑": "Do you have this in a different size?",
            "공항": "Where is the boarding gate for flight KE123?",
            "호텔": "I have a reservation under the name Kim.",
            "테스트": "Hello, nice to meet you!",
            "인사": "How are you doing today?",
        }
        
        # 키워드 매칭으로 문장 선택
        sentence = "How can I help you today?"
        situation_lower = request.situation.lower()
        
        for key, value in example_sentences.items():
            if key in situation_lower:
                sentence = value
                break
        
        return SentenceResponse(
            sentence=sentence,
            situation=request.situation
        )


@app.post("/api/analyze-pronunciation", response_model=FeedbackResponse)
async def analyze_pronunciation(
    audio: UploadFile = File(...),
    original_sentence: str = None
):
    """
    사용자의 음성을 분석하고 피드백을 제공합니다.
    """
    if not original_sentence:
        raise HTTPException(status_code=400, detail="원본 문장이 필요합니다")
    
    try:
        # Speech-to-Text 클라이언트 생성
        client = speech.SpeechClient()
        
        # 오디오 파일 읽기
        audio_content = await audio.read()
        
        # Speech-to-Text 설정
        audio_config = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US",
            enable_automatic_punctuation=True,
            model="default",
        )
        
        # 음성 인식 수행
        response = client.recognize(config=config, audio=audio_config)
        
        if not response.results:
            raise HTTPException(status_code=400, detail="음성을 인식할 수 없습니다")
        
        # 인식된 텍스트 추출
        transcript = response.results[0].alternatives[0].transcript
        confidence = response.results[0].alternatives[0].confidence
        
        # 간단한 피드백 생성 (추후 AI 연동)
        feedback = generate_simple_feedback(original_sentence, transcript, confidence)
        
        # 발음 점수 계산
        pronunciation_score = calculate_pronunciation_score(
            original_sentence.lower(),
            transcript.lower(),
            confidence
        )
        
        return FeedbackResponse(
            transcript=transcript,
            original_sentence=original_sentence,
            feedback=feedback,
            pronunciation_score=pronunciation_score
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발음 분석 실패: {str(e)}")


def generate_simple_feedback(original: str, transcript: str, confidence: float) -> str:
    """
    간단한 피드백 생성
    """
    original_words = set(original.lower().split())
    transcript_words = set(transcript.lower().split())
    matching_words = original_words.intersection(transcript_words)
    match_ratio = len(matching_words) / len(original_words) if original_words else 0
    
    if match_ratio > 0.9:
        return "훌륭합니다! 발음이 매우 정확합니다. 계속 연습하세요!"
    elif match_ratio > 0.7:
        return "좋습니다! 대부분의 단어를 잘 발음하셨습니다. 몇 가지만 더 연습하면 완벽해질 것입니다."
    elif match_ratio > 0.5:
        return "괜찮습니다. 일부 단어의 발음을 다시 확인해보세요. 천천히 또박또박 발음해보세요."
    else:
        return "조금 더 연습이 필요합니다. 문장을 천천히 읽으면서 각 단어를 정확하게 발음해보세요."


def calculate_pronunciation_score(original: str, transcript: str, confidence: float) -> float:
    """
    간단한 발음 점수 계산 (0-100)
    """
    # 단어 단위로 비교
    original_words = set(original.split())
    transcript_words = set(transcript.split())
    
    if not original_words:
        return 0.0
    
    # 일치하는 단어 비율
    matching_words = original_words.intersection(transcript_words)
    word_match_ratio = len(matching_words) / len(original_words)
    
    # 최종 점수: 단어 일치도(60%) + 음성 인식 신뢰도(40%)
    score = (word_match_ratio * 0.6 + confidence * 0.4) * 100
    
    return round(score, 2)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

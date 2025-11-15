// API 엔드포인트 설정
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8080' 
    : 'https://english-practice-backend-65867898884.asia-northeast3.run.app'; // 배포 후 백엔드 URL로 변경

// 전역 변수
let mediaRecorder;
let audioChunks = [];
let currentSentence = '';
let isRecording = false;

// DOM 요소
const situationInput = document.getElementById('situation');
const generateBtn = document.getElementById('generateBtn');
const sentenceSection = document.getElementById('sentenceSection');
const sentenceDisplay = document.getElementById('sentenceDisplay');
const situationDisplay = document.getElementById('situationDisplay');
const recordBtn = document.getElementById('recordBtn');
const recordText = document.getElementById('recordText');
const recordingStatus = document.getElementById('recordingStatus');
const feedbackSection = document.getElementById('feedbackSection');
const scoreValue = document.getElementById('scoreValue');
const transcriptText = document.getElementById('transcriptText');
const feedbackText = document.getElementById('feedbackText');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loadingText');

// 이벤트 리스너
generateBtn.addEventListener('click', generateSentence);
situationInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generateSentence();
    }
});
recordBtn.addEventListener('click', toggleRecording);
tryAgainBtn.addEventListener('click', resetApp);

// 문장 생성
async function generateSentence() {
    const situation = situationInput.value.trim();
    
    if (!situation) {
        alert('상황을 입력해주세요!');
        return;
    }

    showLoading('문장을 생성하는 중...');

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-sentence`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ situation })
        });

        if (!response.ok) {
            throw new Error('문장 생성에 실패했습니다');
        }

        const data = await response.json();
        currentSentence = data.sentence;
        
        sentenceDisplay.textContent = data.sentence;
        situationDisplay.textContent = `상황: ${data.situation}`;
        
        hideLoading();
        sentenceSection.style.display = 'block';
        feedbackSection.style.display = 'none';
        
    } catch (error) {
        hideLoading();
        alert('오류가 발생했습니다: ' + error.message);
        console.error('Error:', error);
    }
}

// 녹음 토글
async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

// 녹음 시작
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                channelCount: 1,
                sampleRate: 48000
            }
        });
        
        // WebM으로 녹음 (Chrome/Edge에서 지원)
        const options = { mimeType: 'audio/webm;codecs=opus' };
        mediaRecorder = new MediaRecorder(stream, options);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
            await analyzePronunciation(audioBlob);
            
            // 스트림 정리
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;
        
        recordBtn.classList.add('recording');
        recordText.textContent = '녹음 중지';
        recordingStatus.textContent = '🔴 녹음 중...';
        
    } catch (error) {
        alert('마이크 접근 권한이 필요합니다!');
        console.error('Error accessing microphone:', error);
    }
}

// 녹음 중지
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        
        recordBtn.classList.remove('recording');
        recordText.textContent = '녹음 시작';
        recordingStatus.textContent = '';
    }
}

// 발음 분석
async function analyzePronunciation(audioBlob) {
    showLoading('발음을 분석하는 중...');

    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('original_sentence', currentSentence);

        const response = await fetch(`${API_BASE_URL}/api/analyze-pronunciation`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('발음 분석에 실패했습니다');
        }

        const data = await response.json();
        
        // 피드백 표시
        displayFeedback(data);
        
        hideLoading();
        feedbackSection.style.display = 'block';
        
        // 부드러운 스크롤
        feedbackSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        hideLoading();
        alert('오류가 발생했습니다: ' + error.message);
        console.error('Error:', error);
    }
}

// 피드백 표시
function displayFeedback(data) {
    // 점수 애니메이션
    animateScore(data.pronunciation_score);
    
    transcriptText.textContent = data.transcript;
    feedbackText.textContent = data.feedback;
}

// 점수 애니메이션
function animateScore(targetScore) {
    let currentScore = 0;
    const increment = targetScore / 50; // 50 프레임으로 나눔
    const duration = 1500; // 1.5초
    const frameTime = duration / 50;

    const timer = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(timer);
        }
        scoreValue.textContent = Math.round(currentScore);
    }, frameTime);
}

// 앱 리셋
function resetApp() {
    situationInput.value = '';
    sentenceSection.style.display = 'none';
    feedbackSection.style.display = 'none';
    currentSentence = '';
    
    // 맨 위로 스크롤
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // 입력 필드에 포커스
    situationInput.focus();
}

// 로딩 표시
function showLoading(message) {
    loadingText.textContent = message;
    loading.style.display = 'flex';
}

// 로딩 숨김
function hideLoading() {
    loading.style.display = 'none';
}

// 페이지 로드 시
window.addEventListener('load', () => {
    situationInput.focus();
    
    // 마이크 권한 확인
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('이 브라우저는 음성 녹음을 지원하지 않습니다.');
    }
});

# OpenAI Computer-Using Agent (CUA) - 브라우저 자동화

이 프로젝트는 OpenAI의 Computer-Using Agent(CUA) API를 사용하여 웹 브라우저 작업을 자동화하는 간단한 예제입니다. 사용자의 자연어 명령을 받아 브라우저에서 실행하는 AI 에이전트를 구현합니다.

![OpenAI CUA 브라우저 자동화](https://raw.githubusercontent.com/openai/openai-assets/master/cua-demo-2.gif)

## 특징

- 자연어로 브라우저 작업 요청 가능
- Google 검색, 날씨 확인, 뉴스 검색 등 다양한 작업 수행
- 브라우저 화면을 실시간으로 확인하며 작업 진행
- 안전 검사 기능으로 위험한 작업 방지
- 키보드/마우스 동작 실시간 모니터링
- OpenAI Agents SDK 기반 학습 도우미 시스템 (터미널 및 웹 인터페이스)

## 필수 사항

- Python 3.8 이상
- OpenAI API 키 (`.env` 파일에 설정)
- Playwright 브라우저 드라이버
- Gradio (웹 인터페이스 사용 시)

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/yourusername/openai-cua-browser.git
cd openai-cua-browser
```

2. 필요한 의존성 설치:
```bash
pip install -r requirements.txt
```

3. Playwright 브라우저 드라이버 설치:
```bash
python setup_playwright.py
```
또는 직접:
```bash
playwright install chromium
```

4. OpenAI API 키 설정:
`.env` 파일을 생성하고 다음 내용을 추가:
```
OPENAI_API_KEY=your_api_key_here
```

5. OpenAI Agents SDK 설치 (학습 도우미 시스템 사용 시):
```bash
pip install openai-agents
```

6. Gradio 설치 (웹 인터페이스 사용 시):
```bash
pip install gradio
```

## 사용 방법

### 브라우저 자동화 에이전트
다음 명령어로 프로그램 실행:
```bash
python cua_browser.py
```

실행하면:
1. Chrome 브라우저 창이 열립니다
2. 프로그램이 수행할 작업을 입력하라는 메시지가 표시됩니다
3. 자연어로 작업을 지시합니다 (예: "서울 날씨 확인해줘", "파이썬 튜토리얼 검색해줘")
4. AI 에이전트가 실시간으로 작업을 수행합니다
5. 작업 완료 후 다음 작업을 입력하거나 종료할 수 있습니다

### 학습 도우미 시스템 (터미널 버전)
OpenAI Agents SDK를 활용한 학습 도우미 시스템을 터미널에서 실행:
```bash
python learning_assistant_agents.py
```

이 시스템은 다음 전문 분야에 대한 질문을 처리합니다:
- 프로그래밍 관련 질문 (Python, JavaScript, Java 등)
- 언어 학습 관련 질문 (영어, 일본어, 중국어 등)
- 역사 관련 질문 (세계사, 한국사)

### 학습 도우미 시스템 (웹 인터페이스)
Gradio 웹 인터페이스를 사용하여 학습 도우미 시스템을 실행:
```bash
python learning_assistant_gradio.py
```

실행 후 브라우저에서 `http://127.0.0.1:7860`으로 접속하여 웹 인터페이스를 통해 질문을 입력할 수 있습니다.

## 작업 예시

### 브라우저 자동화
- "네이버에서 오늘 날씨 확인해줘"
- "OpenAI에 대한 최신 뉴스 찾아줘"
- "유튜브에서 파이썬 강의 검색해줘"
- "서울에서 뉴욕까지 항공권 검색해줘"

### 학습 도우미 시스템
- "Python에서 리스트와 딕셔너리의 차이점은 무엇인가요?"
- "영어에서 현재완료와 과거시제의 차이를 설명해주세요."
- "한국 임진왜란의 주요 원인과 영향은 무엇인가요?"

## 문제 해결

- 브라우저 의존성 오류: `playwright install` 명령어로 모든 필요한 브라우저를 설치하세요
- OpenAI API 오류: `.env` 파일에 API 키가 올바르게 설정되었는지, 그리고 충분한 크레딧이 있는지 확인하세요
- 브라우저가 나타나지 않는 경우: 스크립트에서 `headless=False`로 설정되어 있는지 확인하세요
- Gradio 버전 호환성 문제: `pip install --upgrade gradio`로 최신 버전으로 업데이트하세요

## 안전 주의사항

- 안전 검사가 트리거될 때 확인 메시지가 표시됩니다
- 에이전트가 수행하는 작업을 항상 모니터링하세요
- 민감한 웹사이트나 민감한 작업에 이 에이전트를 사용하지 마세요
- 학습 도우미 시스템은 콘텐츠 가드레일을 적용하여 부적절한 콘텐츠 요청을 자동으로 차단합니다

## 작동 원리

### 브라우저 자동화
1. 사용자의 자연어 명령을 OpenAI의 Computer-Using Agent에 전달
2. AI 모델이 화면을 분석하고 작업을 위한 다음 액션 생성
3. Playwright를 통해 브라우저에서 해당 액션 실행
4. 브라우저 화면 스크린샷 캡처하여 AI에 다시 전송
5. 작업이 완료될 때까지 이 루프 반복

### OpenAI Agents SDK 학습 도우미
1. 사용자의 질문을 입력 받음
2. 가드레일을 통해 부적절한 콘텐츠 여부 확인
3. 분류 에이전트가 질문 유형 파악 (프로그래밍, 언어 학습, 역사)
4. 적합한 전문 에이전트로 질문 전달
5. 전문 에이전트의 답변을 사용자에게 표시
6. Gradio 웹 인터페이스는 위 과정을 웹 브라우저에서 사용 가능하게 구현

## 라이센스

MIT

## 관련 자료

- [OpenAI Computer Use 문서](https://platform.openai.com/docs/guides/computer-use)
- [Playwright 문서](https://playwright.dev/python/docs/intro)
- [OpenAI Agents SDK 문서](https://openai.github.io/openai-agents-python/)
- [Gradio 문서](https://www.gradio.app/docs/) 
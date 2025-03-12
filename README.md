# OpenAI Computer-Using Agent (CUA) - 브라우저 자동화

이 프로젝트는 OpenAI의 Computer-Using Agent(CUA) API를 사용하여 웹 브라우저 작업을 자동화하는 간단한 예제입니다. 사용자의 자연어 명령을 받아 브라우저에서 실행하는 AI 에이전트를 구현합니다.

![OpenAI CUA 브라우저 자동화](https://raw.githubusercontent.com/openai/openai-assets/master/cua-demo-2.gif)

## 특징

- 자연어로 브라우저 작업 요청 가능
- Google 검색, 날씨 확인, 뉴스 검색 등 다양한 작업 수행
- 브라우저 화면을 실시간으로 확인하며 작업 진행
- 안전 검사 기능으로 위험한 작업 방지
- 키보드/마우스 동작 실시간 모니터링

## 필수 사항

- Python 3.8 이상
- OpenAI API 키 (`.env` 파일에 설정)
- Playwright 브라우저 드라이버

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

## 사용 방법

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

## 작업 예시

- "네이버에서 오늘 날씨 확인해줘"
- "OpenAI에 대한 최신 뉴스 찾아줘"
- "유튜브에서 파이썬 강의 검색해줘"
- "서울에서 뉴욕까지 항공권 검색해줘"

## 문제 해결

- 브라우저 의존성 오류: `playwright install` 명령어로 모든 필요한 브라우저를 설치하세요
- OpenAI API 오류: `.env` 파일에 API 키가 올바르게 설정되었는지, 그리고 충분한 크레딧이 있는지 확인하세요
- 브라우저가 나타나지 않는 경우: 스크립트에서 `headless=False`로 설정되어 있는지 확인하세요

## 안전 주의사항

- 안전 검사가 트리거될 때 확인 메시지가 표시됩니다
- 에이전트가 수행하는 작업을 항상 모니터링하세요
- 민감한 웹사이트나 민감한 작업에 이 에이전트를 사용하지 마세요

## 작동 원리

1. 사용자의 자연어 명령을 OpenAI의 Computer-Using Agent에 전달
2. AI 모델이 화면을 분석하고 작업을 위한 다음 액션 생성
3. Playwright를 통해 브라우저에서 해당 액션 실행
4. 브라우저 화면 스크린샷 캡처하여 AI에 다시 전송
5. 작업이 완료될 때까지 이 루프 반복

## 라이센스

MIT

## 관련 자료

- [OpenAI Computer Use 문서](https://platform.openai.com/docs/guides/computer-use)
- [Playwright 문서](https://playwright.dev/python/docs/intro) 
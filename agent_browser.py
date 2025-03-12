import os
import time
import base64
import logging
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from agents import Agent, Runner, function_tool

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 환경 변수 로드
load_dotenv()

# API 키 유효성 검증
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OpenAI API key not set or invalid.")
    raise ValueError("Please set a valid OpenAI API key in your .env file")

# 브라우저 동작 도구 정의
@function_tool
async def navigate_to_url(url: str) -> str:
    """
    지정된 URL로 브라우저를 이동합니다.
    
    Args:
        url: 이동할 웹사이트 URL (예: https://www.naver.com)
    """
    global browser_page
    try:
        # URL이 http로 시작하지 않는 경우 https://를 추가
        if not url.startswith("http"):
            url = "https://" + url
        
        await browser_page.goto(url)
        return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Failed to navigate to {url}: {str(e)}"

@function_tool
async def click_element(x: int, y: int) -> str:
    """
    브라우저에서 지정된 좌표를 클릭합니다.
    
    Args:
        x: 가로 좌표 (픽셀)
        y: 세로 좌표 (픽셀)
    """
    global browser_page
    try:
        await browser_page.mouse.click(x, y)
        return f"Successfully clicked at coordinates ({x}, {y})"
    except Exception as e:
        return f"Failed to click at coordinates ({x}, {y}): {str(e)}"

@function_tool
async def type_text(text: str) -> str:
    """
    브라우저에서 텍스트를 입력합니다.
    
    Args:
        text: 입력할 텍스트
    """
    global browser_page
    try:
        await browser_page.keyboard.type(text)
        return f"Successfully typed: {text}"
    except Exception as e:
        return f"Failed to type text: {str(e)}"

@function_tool
async def press_key(key: str) -> str:
    """
    브라우저에서 특정 키를 누릅니다.
    
    Args:
        key: 누를 키 (예: 'Enter', 'Tab', 'ArrowDown')
    """
    global browser_page
    try:
        await browser_page.keyboard.press(key)
        return f"Successfully pressed key: {key}"
    except Exception as e:
        return f"Failed to press key: {str(e)}"

@function_tool
async def scroll_page(direction: str, amount: int = 300) -> str:
    """
    브라우저 페이지를 스크롤합니다.
    
    Args:
        direction: 스크롤 방향 ('up', 'down', 'left', 'right')
        amount: 스크롤 양 (픽셀 단위)
    """
    global browser_page
    try:
        scroll_x = 0
        scroll_y = 0
        
        if direction.lower() == 'down':
            scroll_y = amount
        elif direction.lower() == 'up':
            scroll_y = -amount
        elif direction.lower() == 'right':
            scroll_x = amount
        elif direction.lower() == 'left':
            scroll_x = -amount
        
        await browser_page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
        return f"Successfully scrolled {direction} by {amount} pixels"
    except Exception as e:
        return f"Failed to scroll: {str(e)}"

@function_tool
async def get_current_url() -> str:
    """현재 브라우저 URL을 반환합니다."""
    global browser_page
    try:
        return browser_page.url
    except Exception as e:
        return f"Failed to get current URL: {str(e)}"

@function_tool
async def wait(seconds: int = 2) -> str:
    """
    지정된 시간(초) 동안 대기합니다.
    
    Args:
        seconds: 대기할 시간(초)
    """
    try:
        await asyncio.sleep(seconds)
        return f"Successfully waited for {seconds} seconds"
    except Exception as e:
        return f"Failed to wait: {str(e)}"

async def get_screenshot() -> str:
    """현재 브라우저 화면의 스크린샷을 base64로 인코딩하여 반환합니다."""
    global browser_page
    try:
        screenshot_bytes = await browser_page.screenshot(full_page=False)
        return base64.b64encode(screenshot_bytes).decode("utf-8")
    except Exception as e:
        logging.error(f"스크린샷 캡처 실패: {e}")
        return ""

async def run_browser_agent(user_task: str):
    """
    브라우저 에이전트를 실행합니다.
    
    Args:
        user_task: 사용자가 요청한 작업
    """
    global browser_page
    
    # 에이전트 생성
    browser_agent = Agent(
        name="브라우저 자동화 도우미",
        instructions="""당신은 웹 브라우저를 자동화하는 도우미입니다.
사용자의 요청에 따라 웹 브라우저를 제어하고 작업을 수행합니다.
제공된 도구를 사용하여 웹 페이지 방문, 클릭, 텍스트 입력, 스크롤 등의 작업을 할 수 있습니다.
작업이 복잡한 경우 단계별로 실행하고 각 단계의 결과를 설명하세요.
사용자의 개인정보를 보호하고 안전한 브라우징을 최우선으로 생각하세요.""",
        tools=[
            navigate_to_url,
            click_element,
            type_text,
            press_key,
            scroll_page,
            get_current_url,
            wait
        ],
        model="gpt-4o"  # 최신 모델 사용
    )
    
    print(f"\n브라우저 자동화 에이전트를 시작합니다. 요청: {user_task}")
    
    # 현재 스크린샷 설명
    screenshot_base64 = await get_screenshot()
    current_url = browser_page.url
    
    # 스크린샷 정보를 포함한 태스크 생성
    task_with_context = f"""작업: {user_task}
현재 URL: {current_url}

위 작업을 수행하기 위해 필요한 브라우저 동작을 실행해주세요."""
    
    # 에이전트 실행
    result = await Runner.run(browser_agent, task_with_context)
    
    print("\n에이전트 응답:")
    print(result.final_output)
    return result.final_output

async def main():
    """메인 함수"""
    global browser_page
    
    print("=" * 50)
    print("OpenAI Agents - 브라우저 자동화")
    print("=" * 50)
    print("\n이 프로그램은 OpenAI Agents SDK를 활용하여 브라우저 작업을 자동화합니다.")
    print("예시 작업:")
    print("- Google에서 Python 튜토리얼 검색")
    print("- 네이버에서 날씨 확인")
    print("- 빙에서 OpenAI 관련 뉴스 찾기")
    
    # Playwright 브라우저 시작
    browser = None
    
    try:
        async with async_playwright() as playwright:
            # 브라우저 실행
            browser = await playwright.chromium.launch(headless=False)
            browser_page = await browser.new_page(viewport={"width": 1024, "height": 768})
            
            # 기본 시작 페이지로 이동
            start_url = os.getenv("DEFAULT_START_URL", "https://www.google.com")
            logging.debug(f"시작 URL: {start_url}")
            await browser_page.goto(start_url)
            
            while True:
                # 사용자 입력 받기
                user_task = input("\n브라우저 작업을 입력하세요 ('exit'로 종료): ")
                
                # 종료 확인
                if user_task.lower() == 'exit':
                    print("프로그램을 종료합니다. 감사합니다!")
                    break
                
                # 빈 입력 처리
                if not user_task.strip():
                    print("유효한 작업을 입력해주세요.")
                    continue
                
                # 한국어 작업에서 네이버로 시작하기
                if ("네이버" in user_task.lower() or "naver" in user_task.lower()) and "google.com" in browser_page.url:
                    print("네이버 관련 태스크를 감지했습니다. 네이버로 이동합니다...")
                    await browser_page.goto("https://www.naver.com")
                
                # 에이전트 실행
                await run_browser_agent(user_task)
    
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다. 종료합니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 브라우저 종료
        if browser:
            await browser.close()

if __name__ == "__main__":
    # 전역 변수 설정
    browser_page = None
    
    # 메인 함수 실행
    asyncio.run(main()) 
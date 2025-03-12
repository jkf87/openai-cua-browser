import os
import time
import base64
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from openai import OpenAI
import logging

# Load environment variables
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# API 키 유효성 검증
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    logging.error("OpenAI API key not set or invalid.")
    raise ValueError("Please set a valid OpenAI API key in your .env file")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)
logging.debug(f"OpenAI API 키: {api_key[:8]}...")

def handle_model_action(page, action):
    """
    Execute the requested action on the browser page.
    """
    action_type = action.type
    
    try:
        if action_type == "click":
            x, y = action.x, action.y
            button = action.button
            print(f"Action: click at ({x}, {y}) with button '{button}'")
            if button != "left" and button != "right":
                button = "left"
            page.mouse.click(x, y, button=button)

        elif action_type == "scroll":
            x, y = action.x, action.y
            # Use getattr for optional parameters
            scroll_x = getattr(action, "scroll_x", 0)
            scroll_y = getattr(action, "scroll_y", 0)
            print(f"Action: scroll at ({x}, {y}) with offsets ({scroll_x}, {scroll_y})")
            page.mouse.move(x, y)
            page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")

        elif action_type == "keypress":
            keys = action.keys
            # 키 이름 매핑 정의
            key_mapping = {
                "CTRL": "Control",
                "CMD": "Meta",
                "COMMAND": "Meta",
                "ALT": "Alt",
                "SHIFT": "Shift",
                "ESC": "Escape",
                "ESCAPE": "Escape",
                "ENTER": "Enter",
                "RETURN": "Enter",
                "SPACE": " ",
                "SPACEBAR": " ",
                "TAB": "Tab",
                "BACKSPACE": "Backspace",
                "DELETE": "Delete",
                "DEL": "Delete",
                "UP": "ArrowUp",
                "DOWN": "ArrowDown",
                "LEFT": "ArrowLeft",
                "RIGHT": "ArrowRight",
                "PAGEUP": "PageUp",
                "PAGEDOWN": "PageDown",
                "HOME": "Home",
                "END": "End",
                "INSERT": "Insert",
                "INS": "Insert"
            }
            
            for k in keys:
                # 대문자로 변환 후 매핑에서 확인
                mapped_key = key_mapping.get(k.upper(), k)
                print(f"Action: keypress '{k}' -> '{mapped_key}'")
                try:
                    page.keyboard.press(mapped_key)
                except Exception as e:
                    print(f"  - Error pressing key '{mapped_key}': {e}")
                    # 혹시 조합키인 경우 처리 시도 (예: "ctrl+a")
                    if "+" in k:
                        parts = k.split("+")
                        if len(parts) == 2:
                            modifier = key_mapping.get(parts[0].upper(), parts[0])
                            key = key_mapping.get(parts[1].upper(), parts[1])
                            print(f"  - Trying as modifier+key: {modifier}+{key}")
                            try:
                                page.keyboard.press(f"{modifier}+{key}")
                                print(f"  - Successfully pressed: {modifier}+{key}")
                            except Exception as e2:
                                print(f"  - Error with modifier+key: {e2}")
        
        elif action_type == "type":
            text = action.text
            print(f"Action: type text: {text}")
            page.keyboard.type(text)
        
        elif action_type == "wait":
            # Use getattr for optional parameters
            duration = getattr(action, "duration", 2)
            print(f"Action: wait for {duration} seconds")
            time.sleep(duration)

        elif action_type == "screenshot":
            print("Action: screenshot")
            # Nothing to do here as we take screenshots after every action

        elif action_type == "navigate":
            url = action.url
            print(f"Action: navigate to URL '{url}'")
            logging.debug(f"Navigating to: {url}")
            # URL이 http로 시작하지 않는 경우 http://를 추가
            if not url.startswith("http"):
                url = "https://" + url
            page.goto(url)

        else:
            print(f"Unrecognized action: {action_type}")

        # Allow a short time for the action to complete
        time.sleep(0.5)
        return True

    except Exception as e:
        print(f"Error handling action {action_type}: {e}")
        return False

def get_screenshot(page):
    """
    Take a screenshot of the current page and return base64 encoded image.
    """
    screenshot_bytes = page.screenshot(full_page=False)
    return base64.b64encode(screenshot_bytes).decode("utf-8")

def computer_use_loop(page, response):
    """
    Main loop for executing computer actions based on model responses.
    """
    try:
        while True:
            # Check for computer calls in the response
            computer_calls = [item for item in response.output if item.type == "computer_call"]
            
            if not computer_calls:
                print("No more computer calls. Task completed or assistant is responding with text.")
                # Print the final text response if there's any
                for item in response.output:
                    if hasattr(item, 'content') and item.content:
                        print(f"Assistant: {item.content}")
                break
            
            # Get the latest computer call
            computer_call = computer_calls[0]
            call_id = computer_call.call_id
            action = computer_call.action
            
            # Check for pending safety checks
            pending_safety_checks = computer_call.pending_safety_checks
            acknowledged_safety_checks = []
            
            if pending_safety_checks:
                print("\nSafety checks detected:")
                for check in pending_safety_checks:
                    print(f"- {check.code}: {check.message}")
                    acknowledged_safety_checks.append(check)
                
                user_confirmation = input("Do you want to acknowledge these safety checks and continue? (y/n): ")
                if user_confirmation.lower() != 'y':
                    print("Operation cancelled by user.")
                    break
            
            # Execute the action
            success = handle_model_action(page, action)
            if not success:
                print("Failed to execute action. Stopping loop.")
                break
            
            # Get current URL for better safety checks
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Take a new screenshot
            screenshot_base64 = get_screenshot(page)
            
            # Send the updated state back to the model
            print("Sending updated state to the model...")
            response = client.responses.create(
                model="computer-use-preview",
                previous_response_id=response.id,
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": 1024,
                    "display_height": 768,
                    "environment": "browser"
                }],
                input=[
                    {
                        "type": "computer_call_output",
                        "call_id": call_id,
                        "acknowledged_safety_checks": acknowledged_safety_checks,
                        "output": {
                            "type": "computer_screenshot",
                            "image_url": f"data:image/png;base64,{screenshot_base64}"
                        },
                        "current_url": current_url
                    }
                ],
                truncation="auto"
            )
    except Exception as e:
        print(f"Error in computer use loop: {e}")
        import traceback
        traceback.print_exc()

def start_browsing_session(user_task):
    """
    Start a browser session with the computer use agent.
    
    Args:
        user_task: Description of the task to perform
    """
    print(f"\nStarting Computer-Using Agent with task: {user_task}")
    
    # Browser setup
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)  # Set to True for headless mode
        page = browser.new_page(viewport={"width": 1024, "height": 768})
        
        # 환경변수에서 시작 URL 설정
        start_url = os.getenv("DEFAULT_START_URL", "https://www.google.com")
        logging.debug(f"시작 URL: {start_url}")
        
        # 한국어 작업이 많다면 네이버로 시작할지 확인
        if "네이버" in user_task.lower() or "naver" in user_task.lower():
            start_url = "https://www.naver.com"
            logging.debug(f"네이버 관련 태스크 감지, 시작 URL 변경: {start_url}")
        
        # URL로 이동
        try:
            logging.debug(f"페이지 이동 시도: {start_url}")
            page.goto(start_url)
            logging.debug(f"현재 URL: {page.url}")
        except Exception as e:
            logging.error(f"페이지 이동 실패: {e}")
            # 실패 시 구글로 대체
            page.goto("https://www.google.com")
        
        # Take initial screenshot
        screenshot_base64 = get_screenshot(page)
        
        # Initialize the CUA with the first request
        try:
            print("Initializing Computer-Using Agent...")
            response = client.responses.create(
                model="computer-use-preview",
                instructions=f"You are a helpful web browsing assistant. {user_task}",
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": 1024,
                    "display_height": 768,
                    "environment": "browser"
                }],
                input=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": user_task
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{screenshot_base64}"
                            }
                        ]
                    }
                ],
                truncation="auto"
            )
            
            # Start the computer use loop
            computer_use_loop(page, response)
            
        except Exception as e:
            print(f"Error during browsing session: {e}")
            import traceback
            traceback.print_exc()
        
        # Close the browser
        browser.close()
        print("Session completed.\n")

def main():
    """
    Main function to start the browsing session.
    """
    print("=" * 50)
    print("OpenAI Computer-Using Agent (CUA) - Browser Automation")
    print("=" * 50)
    print("\nThis program allows you to automate browser tasks using OpenAI's CUA.")
    print("Example tasks:")
    print("- Search for Python tutorials on Google")
    print("- Check the weather in Seoul")
    print("- Look up news about OpenAI on Bing")
    print("- Book a flight ticket to New York")
    
    logging.debug("Starting Computer-Using Agent...")
    
    try:
        while True:
            # Get user input for the task
            user_task = input("\nEnter your browser task (or 'exit' to quit): ")
            
            # Check if user wants to exit
            if user_task.lower() == 'exit':
                print("Exiting program. Goodbye!")
                break
                
            # Skip empty inputs
            if not user_task.strip():
                print("Please enter a valid task.")
                continue
                
            # Start the browsing session with the user's task
            start_browsing_session(user_task)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting gracefully.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nThank you for using the Computer-Using Agent!")

if __name__ == "__main__":
    main() 
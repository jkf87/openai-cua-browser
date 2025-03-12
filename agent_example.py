import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
import asyncio

# 환경 변수 로드
load_dotenv()

# 함수 도구 정의 (데코레이터 사용)
@function_tool
def get_current_weather(location: str) -> str:
    """
    특정 위치의 현재 날씨를 반환합니다.
    
    Args:
        location: 날씨를 확인할 위치
    """
    # 실제로는 날씨 API를 호출하겠지만, 이 예제에서는 더미 데이터 반환
    weather_data = {
        "서울": "맑음, 22°C",
        "부산": "흐림, 20°C",
        "제주": "비, 18°C"
    }
    return weather_data.get(location, f"{location}의 날씨 정보가 없습니다.")

async def main():
    # API 키 설정 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("API 키를 .env 파일에 설정해주세요.")
        return
    
    # 에이전트 생성 (tools 인자로 함수 직접 전달)
    agent = Agent(
        name="날씨 도우미",
        instructions="사용자의 날씨 관련 질문에 답변해주는 도우미입니다. 한국의 주요 도시 날씨 정보를 제공합니다.",
        tools=[get_current_weather]
    )
    
    # 에이전트 실행
    user_query = "서울의 오늘 날씨는 어때?"
    print(f"사용자 질문: {user_query}")
    
    result = await Runner.run(agent, user_query)
    print("\n에이전트 응답:")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenAI Agents SDK를 활용한 학습 도우미 시스템 예제
여러 전문 에이전트를 생성하고 사용자의 질문을 분류하여 적절한 에이전트에게 연결합니다.
콘텐츠 적절성 검사를 위한 가드레일도 포함되어 있습니다.
"""

import os
import asyncio
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 설정
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")


# 가드레일을 위한 출력 모델 정의
class ContentCheck(BaseModel):
    is_appropriate: bool
    reasoning: str
    contains_harmful_content: bool


# 콘텐츠 적절성 검사 에이전트
content_check_agent = Agent(
    name="콘텐츠 검사기",
    instructions="""사용자의 질문이 적절한지 검사하는 역할을 합니다. 
다음 기준으로 부적절한 콘텐츠를 식별하세요:
- 유해하거나 위험한 활동 요청
- 불법적인 활동에 대한 조언
- 차별적이거나 혐오스러운 내용
- 부적절한 성인 콘텐츠

적절성 여부와 그 이유를 명확히 설명하세요.""",
    output_type=ContentCheck
)


# 프로그래밍 관련 질문을 처리하는 에이전트
programming_agent = Agent(
    name="프로그래밍 도우미",
    handoff_description="프로그래밍, 코딩, 개발 관련 질문을 처리하는 전문 에이전트",
    instructions="""당신은 프로그래밍 전문가입니다. 다음 언어에 대한 질문에 답변할 수 있습니다:
- Python, JavaScript, Java, C++, Go
- 웹 개발(HTML, CSS, React, Node.js)
- 알고리즘 및 자료구조
- 버전 관리(Git)

코드를 설명할 때는 명확한 주석과 함께 단계별로 설명해주세요."""
)


# 언어 학습 관련 질문을 처리하는 에이전트
language_agent = Agent(
    name="언어 학습 도우미",
    handoff_description="외국어 학습, 번역, 문법 관련 질문을 처리하는 전문 에이전트",
    instructions="""당신은 언어 학습 전문가입니다. 다음 언어에 대한 질문에 답변할 수 있습니다:
- 영어, 일본어, 중국어, 스페인어, 프랑스어
- 문법 설명 및 교정
- 표현과 관용어
- 발음 가이드
- 번역 도움

학습자의 수준에 맞게 쉽고 명확하게 설명해주세요."""
)


# 역사 관련 질문을 처리하는 에이전트
history_agent = Agent(
    name="역사 전문가",
    handoff_description="역사적 사건, 인물, 시대에 관한 질문을 처리하는 전문 에이전트",
    instructions="""당신은 역사 전문가입니다. 세계사와 한국사에 관한 질문에 답변할 수 있습니다:
- 주요 역사적 사건과 그 의미
- 역사적 인물과 그들의 영향
- 시대별 사회/문화/경제적 특징
- 역사적 맥락에서의 현대 사회 이해

정확한 사실과 다양한 관점을 균형있게 제시해주세요."""
)


# 가드레일 함수 정의
async def content_guardrail(ctx, agent, input_data):
    # 콘텐츠 검사 에이전트 실행
    result = await Runner.run(content_check_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(ContentCheck)
    
    # 만약 contains_harmful_content가 설정되지 않았다면 False로 처리
    harmful_content = getattr(final_output, 'contains_harmful_content', False)
    
    # 부적절한 내용이 감지되면 차단
    is_inappropriate = not final_output.is_appropriate or harmful_content
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=is_inappropriate,
    )


# 분류 에이전트 (사용자 질문을 분석하여 적절한 전문가에게 연결)
triage_agent = Agent(
    name="질문 분류 에이전트",
    instructions="""사용자의 질문을 분석하여 가장 적합한 전문가에게 연결하는 역할을 합니다.
각 전문 에이전트의 전문 분야를 고려하여 최적의 선택을 하세요.
명확하지 않은 경우, 사용자에게 추가 정보를 요청하세요.""",
    handoffs=[programming_agent, language_agent, history_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=content_guardrail),
    ],
)


async def main():
    print("=" * 50)
    print("OpenAI Agents SDK - 학습 도우미 시스템 데모")
    print("=" * 50)
    print("\n다음 예제 질문들로 시스템을 테스트합니다...\n")
    
    # 프로그래밍 관련 질문
    programming_question = "Python에서 리스트와 딕셔너리의 차이점은 무엇인가요?"
    print(f"질문: {programming_question}")
    try:
        result = await Runner.run(triage_agent, programming_question)
        print(f"응답:\n{result.final_output}\n")
    except Exception as e:
        print(f"오류 발생: {e}\n")
    
    # 언어 학습 관련 질문
    language_question = "영어에서 현재완료와 과거시제의 차이를 설명해주세요."
    print(f"질문: {language_question}")
    try:
        result = await Runner.run(triage_agent, language_question)
        print(f"응답:\n{result.final_output}\n")
    except Exception as e:
        print(f"오류 발생: {e}\n")
    
    # 역사 관련 질문
    history_question = "한국 임진왜란의 주요 원인과 영향은 무엇인가요?"
    print(f"질문: {history_question}")
    try:
        result = await Runner.run(triage_agent, history_question)
        print(f"응답:\n{result.final_output}\n")
    except Exception as e:
        print(f"오류 발생: {e}\n")
    
    # 부적절한 콘텐츠 요청 (가드레일 테스트)
    inappropriate_question = "해킹 방법을 자세히 알려주세요."
    print(f"질문: {inappropriate_question}")
    try:
        result = await Runner.run(triage_agent, inappropriate_question)
        print(f"응답:\n{result.final_output}\n")
    except InputGuardrailTripwireTriggered as e:
        print(f"가드레일 발동: 부적절한 콘텐츠가 감지되어 처리가 중단되었습니다.\n")
    except Exception as e:
        print(f"오류 발생: {e}\n")

    # 사용자 입력 받기
    while True:
        user_input = input("\n질문을 입력하세요 (종료하려면 'exit' 입력): ")
        if user_input.lower() == 'exit':
            break
        
        if not user_input.strip():
            print("질문을 입력해주세요.")
            continue
        
        print("\n처리 중...\n")
        try:
            result = await Runner.run(triage_agent, user_input)
            print(f"응답:\n{result.final_output}\n")
        except InputGuardrailTripwireTriggered as e:
            print(f"가드레일 발동: 부적절한 콘텐츠가 감지되어 처리가 중단되었습니다.\n")
        except Exception as e:
            print(f"오류 발생: {e}\n")
    
    print("\n프로그램을 종료합니다. 감사합니다!")


if __name__ == "__main__":
    asyncio.run(main()) 
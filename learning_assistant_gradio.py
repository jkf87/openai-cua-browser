#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenAI Agents SDK를 활용한 학습 도우미 시스템 예제 - Gradio 웹 인터페이스 버전
여러 전문 에이전트를 생성하고 사용자의 질문을 분류하여 적절한 에이전트에게 연결합니다.
콘텐츠 적절성 검사를 위한 가드레일도 포함되어 있습니다.
"""

import os
import asyncio
import gradio as gr
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


# Gradio 인터페이스 함수
async def process_question(question, history):
    history = history or []
    
    if not question.strip():
        yield history + [[question, "질문을 입력해주세요."]]
        return
    
    try:
        # 상태 업데이트
        yield history + [[question, "처리 중..."]]
        
        # 에이전트 실행
        result = await Runner.run(triage_agent, question)
        answer = result.final_output
        
        # 결과 반환
        yield history + [[question, answer]]
    
    except InputGuardrailTripwireTriggered:
        yield history + [[question, "⚠️ 가드레일 발동: 부적절한 콘텐츠가 감지되어 처리가 중단되었습니다."]]
    
    except Exception as e:
        yield history + [[question, f"오류 발생: {str(e)}"]]


# 예제 질문 목록
example_questions = [
    ["Python에서 리스트와 딕셔너리의 차이점은 무엇인가요?"],
    ["영어에서 현재완료와 과거시제의 차이를 설명해주세요."],
    ["한국 임진왜란의 주요 원인과 영향은 무엇인가요?"]
]


# Gradio 애플리케이션 실행
def create_demo():
    with gr.Blocks(title="학습 도우미 에이전트") as demo:
        gr.Markdown("""
        # 💬 학습 도우미 에이전트
        이 시스템은 프로그래밍, 언어 학습, 역사 분야의 질문에 답변할 수 있는 AI 에이전트입니다.
        OpenAI Agents SDK를 사용하여 구현되었습니다.
        """)
        
        with gr.Row():
            with gr.Column(scale=7):
                chatbot = gr.Chatbot(
                    show_label=False,
                    avatar_images=(None, "🤖"),
                    height=500
                )
                
                with gr.Row():
                    question = gr.Textbox(
                        placeholder="질문을 입력하세요...",
                        show_label=False,
                        scale=9
                    )
                    submit_btn = gr.Button("전송", scale=1, variant="primary")
                
                clear_btn = gr.Button("대화 내용 지우기")
            
            with gr.Column(scale=3):
                gr.Markdown("""
                ### 🔍 주제별 전문 에이전트
                
                이 시스템은 질문 유형에 따라 자동으로 적절한 전문 에이전트를 선택합니다:
                
                - **🖥️ 프로그래밍 도우미**: 코딩, 개발, 알고리즘 관련 질문
                - **🗣️ 언어 학습 도우미**: 외국어, 문법, 번역 관련 질문
                - **📜 역사 전문가**: 역사적 사건, 인물, 시대 관련 질문
                
                ### 🛡️ 안전 장치
                
                모든 질문은 콘텐츠 가드레일을 통과한 후 처리됩니다.
                부적절한 콘텐츠는 자동으로 차단됩니다.
                """)
                
                gr.Examples(
                    examples=example_questions,
                    inputs=question,
                    label="예제 질문"
                )
        
        # 이벤트 처리
        submit_btn.click(
            fn=process_question,
            inputs=[question, chatbot],
            outputs=chatbot,
            api_name="submit"
        ).then(
            fn=lambda: "",
            inputs=None,
            outputs=question
        )
        
        question.submit(
            fn=process_question,
            inputs=[question, chatbot],
            outputs=chatbot,
            api_name="submit_text"
        ).then(
            fn=lambda: "",
            inputs=None,
            outputs=question
        )
        
        clear_btn.click(
            fn=lambda: None,
            inputs=None,
            outputs=chatbot,
            api_name="clear"
        )
    
    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.queue(max_size=20).launch(
        share=False,          # 공개 URL 생성 여부
        server_name="0.0.0.0", # 모든 IP에서 접근 가능
        server_port=7860,      # 기본 Gradio 포트
        debug=True
    ) 
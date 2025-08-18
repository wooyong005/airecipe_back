# 정용우 전부 추가
# pip install google-generativeai # 제미나이 라이브러리 설치. 
# pip install --upgrade google-generativeai # 최신 라이브러리 업그레이드 

# https://makersuite.google.com/app/apikey 접속 → 로그인 → 키 발급(API키 발급)

# .env 사용하다가 못 불러와서 키를 직접 넣음



# import os
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

import google.generativeai as genai # # 구글 Gemini API 라이브러리 불러오기

# 직접 API 키 삽입 # .env 오류 #  (보안상 실제 서비스에서는 .env 파일에 저장하는 것이 권장됨)
genai.configure(api_key="your-key")  # 

model = genai.GenerativeModel("gemini-1.5-flash")  # # 사용할 모델을 지정

def ask_chatbot(message: str) -> str: 
    """
    사용자가 입력한 메시지를 바탕으로
    요리 전문가처럼 레시피를 단계별로 설명해주는 함수
    """    # prompt에 따라 챗봇 대답의 질이 바뀜
    prompt = f"'{message}'에 대해 요리 전문가처럼 자세하고 친절하게 요리 레시피를 단계별로 설명해줘. 칼로리,지방 같은 영양성분과 재료를 먼저 알려줘. 그 다음에는 1단계,2단계...단계별로 요리 순서를 알려줘"
    response = model.generate_content(prompt)
    return response.text.strip()












########## 아래는  무시. # 지울거임

# # 환경 변수 로드 # .env에 있는 키 가져오기 
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# if not GOOGLE_API_KEY:
#     raise Exception("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")

# # Google Generative AI 구성
# genai.configure(api_key=GOOGLE_API_KEY)

# #  # model 다르게 가능.
# model = model = genai.GenerativeModel("gemini-pro")

# # FastAPI 애플리케이션 생성
# app = FastAPI(title="Gemini 챗봇")

# # 요청 모델 정의
# class ChatRequest(BaseModel):
#     prompt: str

# @app.post("/chat/")
# async def chat(request: ChatRequest):
#     try:
#         # 사용자 프롬프트 추출
#         user_prompt = request.prompt

#         # 모델을 사용하여 응답 생성
#         response = model.generate_content(
#             user_prompt,
#             generation_config=genai.types.GenerationConfig(
#                 candidate_count=1,
#                 temperature=0.7
#             )
#         )

#         # 응답 처리
#         if response.candidates and response.candidates[0].content.parts:
#             generated_text = ''.join([part.text for part in response.candidates[0].content.parts])
#         else:
#             raise HTTPException(status_code=500, detail="유효한 응답 내용을 찾을 수 없습니다.")

#         return {"reply": generated_text.strip()}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
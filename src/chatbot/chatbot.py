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
    """    # prompt에 따라 챗봇 대답의 질이 바뀜 # 비 스트리밍(완성형) 함수 
    prompt = f"'{message}'에 대해 요리 전문가처럼 자세하고 친절하게 요리 레시피를 단계별로 설명해줘. 칼로리,지방 같은 영양성분과 재료를 먼저 알려줘. 그 다음에는 1단계,2단계...단계별로 요리 순서를 알려줘"
    response = model.generate_content(prompt)
    return response.text.strip()
















# 정용우 전부 추가
# chatbot/chatbot.py


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
genai.configure(api_key="AIzaSyDnMIpa9qzRUdMvX5FvH4v13JOhWfjzkIs")  # 

gemini_model = genai.GenerativeModel("gemini-1.5-flash")  # # 사용할 모델을 지정 # "gemini-2.5-pro" 사용해보기 # gemini-1.5-flash

def ask_chatbot(message: str) -> str: 
    """
    사용자가 입력한 메시지를 바탕으로
    요리 전문가처럼 레시피를 단계별로 설명해주는 함수
    """    # prompt에 따라 챗봇 대답의 질이 바뀜  
    prompt = f"'{message}'에 대해 요리 전문가처럼 자세하고 친절하게 요리 레시피를 단계별로 설명해줘. 칼로리,지방 같은 영양성분과 재료를 먼저 알려줘. 그 다음에는 1단계,2단계...단계별로 요리 순서를 알려줘"
    response = gemini_model.generate_content(prompt, stream=True) # gemini api 호출
    # return response.text.strip() # 결과 텍스트 반환

    final_text = ""
    for no, chunk in enumerate(response, start=1):
        if chunk.text:
            print(f"{no}: {chunk.text}")   # 조각별 출력
            print("=" * 50)
            final_text += chunk.text       # 전체 답변 합치기

    return final_text.strip()

















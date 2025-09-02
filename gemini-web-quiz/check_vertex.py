import vertexai
from vertexai.generative_models import GenerativeModel
import os

# --- 진단할 프로젝트 정보 ---
project_id = "gen-lang-client-0589864401"
location = "asia-northeast3"
# --- 마지막 테스트를 위해 다른 계열의 모델로 변경합니다 ---
model_name = "gemini-1.5-flash-preview-0514"

print("--- Vertex AI 연결 최종 진단 ---")
print(f"프로젝트: '{project_id}', 리전: '{location}'")
print(f"모델: '{model_name}'으로 마지막 연결을 시도합니다.")


try:
    print("\n[단계 1] vertexai.init() 함수 호출...")
    vertexai.init(project=project_id, location=location)
    print("✅ [성공] Vertex AI 초기화 완료.")

    print("\n[단계 2] GenerativeModel() 클래스 로드...")
    model = GenerativeModel(model_name)
    print("✅ [성공] 모델 로드 완료.")

    print("\n[단계 3] model.generate_content() API 호출...")
    response = model.generate_content("Hello, this is a final test.")
    print("✅ [성공] API 호출 완료.")
    
    print("\n--- 🎉 진단 성공 ---")
    print("실행 환경과 인증 정보가 올바르게 설정되었습니다.")
    print("Gemini 응답:", response.text)

except Exception as e:
    print("\n--- ❌ 진단 실패 ---")
    print("오류가 발생했습니다. 아래 상세 내용을 확인해주세요:")
    print("========================================================")
    print(e)
    print("========================================================")
    print("\n--- 최종 권장 사항 ---")
    print("코드가 아닌 Google Cloud 계정 또는 환경 문제입니다.")
    print("1. 완전히 다른 Google 계정(예: 개인 Gmail 계정)으로 새 프로젝트를 만들어 다시 시도해보세요.")
    print("2. 만약 현재 계정을 꼭 사용해야 한다면, Google Cloud 지원팀에 문의하여 프로젝트의 Vertex AI 모델 접근 권한을 확인해야 합니다.")


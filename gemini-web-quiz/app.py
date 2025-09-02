import os
from flask import Flask, render_template, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Flask 앱 및 기본 경로 설정 ---
app = Flask(__name__)
APP_DIR = os.path.dirname(os.path.abspath(__file__)) # gemini-web-quiz 폴더
PROJECT_ROOT = os.path.dirname(APP_DIR) # tech-interview-for-developer 폴더

# --- (핵심) 여기서 학습할 폴더 경로를 직접 선택하세요! ---
# 프로젝트 최상위(tech-interview-for-developer) 폴더로부터의 상대 경로를 입력합니다.
# [균형 추천] 시스템 SW 직무 면접을 위한 핵심 범위
INCLUDED_PATHS = [
    "Computer Science/Operating System",
    "Computer Science/Computer Architecture",
    "Computer Science/Data Structure",
    "Algorithm",
    "Linux",
    "Language", # C, C++, Java 등 핵심 언어 지식 포함
    "ETC",      # '임베디드 시스템.md' 학습을 위해 포함
]
# ----------------------------------------------------

# --- Gemini 라이브러리 초기화 ---
PROJECT_ID = "cs-quiz-bot-470405" 
LOCATION = "us-central1"

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    gemini_model = GenerativeModel("gemini-2.5-flash")
    print("✅ Vertex AI 및 Gemini 모델이 성공적으로 초기화되었습니다.")
except Exception as e:
    print(f"🚨 Vertex AI 초기화 중 오류 발생: {e}")
    gemini_model = None

# --- (핵심 변경) 지정된 경로 목록에서 학습 자료를 로드하는 함수 ---
def load_topics_from_paths(root_dir, paths_to_include):
    """지정된 상대 경로 목록에 있는 모든 .md 파일 내용을 읽어 하나로 합칩니다."""
    all_content = ""
    print("선택된 학습 자료 로드를 시작합니다...")
    
    # INCLUDED_PATHS 리스트를 순회합니다.
    for relative_path in paths_to_include:
        target_path = os.path.join(root_dir, relative_path)
        
        if not os.path.isdir(target_path):
            print(f"  - ⚠️ 경고: '{relative_path}' 경로를 찾을 수 없습니다. 건너뜁니다.")
            continue
            
        print(f"  - '{relative_path}' 경로를 탐색합니다...")
        for root, _, files in os.walk(target_path):
            for filename in files:
                if filename.endswith(".md"):
                    file_path = os.path.join(root, filename)
                    # 표시될 경로를 일관성 있게 프로젝트 루트 기준으로 변경
                    display_path = os.path.relpath(file_path, root_dir)
                    all_content += f"\n\n---\n# 학습 자료: {display_path}\n---\n\n"
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            all_content += f.read()
                        print(f"    - 로드 완료: {display_path}")
                    except Exception as e:
                        print(f"    - 🚨 파일 읽기 오류: {display_path} ({e})")
                        all_content += f"오류: {display_path} 파일을 읽을 수 없습니다.\n"

    if not all_content:
        return "# 경고: 로드할 학습 자료(.md 파일)가 선택되지 않았거나, 폴더 내에 파일이 없습니다."
        
    return all_content

# 앱이 실행될 때 딱 한 번만 선택된 경로의 토픽을 읽어서 변수에 저장합니다.
ALL_CS_CONTENT = load_topics_from_paths(PROJECT_ROOT, INCLUDED_PATHS)
print(f"✅ 총 {len(ALL_CS_CONTENT.splitlines())} 줄의 학습 자료 로드 완료!")


@app.route('/')
def index():
    return render_template('index.html')

# /ask 라우트는 이전 코드와 동일하게 유지됩니다.
@app.route('/ask', methods=['POST'])
def ask_gemini():
    if not gemini_model:
        return jsonify({'answer': "오류: Gemini 모델이 초기화되지 않았습니다. app.py 로그를 확인해주세요."})
    # ... (이하 동일)
    data = request.json
    conversation_history = data.get('question', '')
    
    prompt = f"""당신은 삼성전자 MX사업부의의 안드로이드 시스템 SW 개발 전문 기술 면접관입니다. 당신의 역할은 신입 개발자 지원자의 CS 지식을 테스트하는 것입니다.
    
    [규칙]
    1. 아래 제공된 [전체 학습 자료]의 내용만을 기반으로 질문해야 합니다.
    2. 학습 자료는 여러 주제를 포함하고 있습니다. 주제를 넘나들며 자유롭게 질문하여 실제 면접과 같은 경험을 제공해주세요.
    3. 이전 [대화 내용]을 참고하여 자연스럽게 대화를 이어가세요. 꼬리 질문을 하거나, 완전히 다른 주제로 넘어가도 좋습니다. 단, 지원자가 완전히 이해하고 있는지 판단하고 진행해야 합니다.
    4. 질문은 반드시 한 번에 하나씩만 해주세요.
    5. 지원자의 답변을 받으면, 답변이 잘했는지 부족한지 핵심을 짚어 피드백을 주고, 관련된 추가 질문이나 다음 질문으로 넘어가세요.
    6. 딱딱한 말투 대신, 실제 면접처럼 부드럽고 친절한 말투를 사용해주세요. ("~에 대해 설명해주시겠어요?", "~님께서는 어떻게 생각하시나요?")
    7. 마크다운 문법이나 이모지 사용은 금지합니다.
    8. 질문 시작 전 어떤 파일에서 가져온 내용인지 괄호로 표시해주세요. (ex. [Computer Science/Operating System])

    [전체 학습 자료]
    {ALL_CS_CONTENT}
    
    [대화 내용]
    {conversation_history}
    
    이제 면접관으로서 다음 질문을 해주세요.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        return jsonify({'answer': response.text})
    except Exception as e:
        return jsonify({'answer': f"Gemini API 호출 중 오류가 발생했습니다: {str(e)}"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
import os
import re

def clean_and_prepare_text_for_doccano_final_v2(input_filepath, output_filepath):
    """
    주어진 텍스트 파일에서 다음을 수행합니다:
    1. 한 줄에 숫자(0-9) 하나만 있는 라인을 삭제합니다.
    2. '2021년 소방시설법령 질의회신집' 문자열을 제거합니다.
    3. '질의 N.' (또는 '질의 N')으로 시작하는 줄 앞에 빈 줄(\n\n)을 추가합니다.
       (단, 파일의 맨 처음 나오는 '질의 1.' 앞에는 추가하지 않습니다.)
       이때, 각 '질의 N.' 블록이 정확히 '\n\n'으로 구분되도록 합니다.
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines() # 파일을 줄 단위로 읽어옵니다.

        temp_content = [] # 임시로 클리닝된 줄을 저장할 리스트
        for line in lines:
            # 1단계: '2021년 소방시설법령 질의회신집' 문자열 제거
            line = line.replace('2021년 소방시설법령 질의회신집', '')

            # 2단계: 한 줄에 숫자 하나만 있는 라인 삭제
            if line.strip().isdigit() and len(line.strip()) == 1:
                continue # 해당 줄은 건너뛰고 다음 줄로 넘어갑니다.

            # 모든 줄의 양쪽 공백 제거 후 임시 리스트에 추가 (원래 줄바꿈도 제거)
            temp_content.append(line.strip())

        # 임시 리스트의 줄들을 하나의 문자열로 결합 (각 줄 사이에 공백 1개로 연결)
        cleaned_raw_text = ' '.join(temp_content).strip()

        # 3단계: '질의 N.' 앞에 빈 줄 추가
        # '질의 N.' (또는 '질의 N') 패턴을 찾아서 '\n\n질의 N.'으로 교체합니다.
        # 단, 파일의 맨 처음 나오는 '질의 1.' 앞에는 추가하지 않습니다.

        # re.sub의 repl 매개변수에 함수를 사용하여 동적 교체
        def replace_query_marker(match):
            # match.start() == 0 이면 파일의 맨 처음 '질의 N.'입니다.
            if match.start() == 0:
                return match.group(0) # '질의 N.' 자체를 반환 (앞에 아무것도 안 붙임)
            else:
                return '\n\n' + match.group(0) # 그 외의 '질의 N.' 앞에는 '\n\n'을 붙임

        # 패턴: '질의' 다음에 공백(0개 이상), 숫자(1개 이상), 점(선택적)
        final_content = re.sub(r'질의\s*\d+\.?', replace_query_marker, cleaned_raw_text)

        final_content = re.sub(r'(회신\s*\d\.?)', r'\n\1', final_content)
        
        final_content = re.sub(r'▣.*', '', final_content)  # '▣'로 시작하는 줄 제거
        
        final_content = re.sub(r'\s\d{2,3}\s', '', final_content)  # 숫자(2-3자리) 제거

        # 최종적으로 문자열의 시작과 끝에 불필요한 공백/개행을 제거
        final_content = final_content.strip()

        with open(output_filepath, 'w', encoding='utf-8') as f_out:
            f_out.write(final_content)

        print(f"파일이 성공적으로 처리되어 '{output_filepath}'에 저장되었습니다.")
        print("이 파일을 Doccano에 'Plain Text' 형식으로 가져오시면 됩니다.")

    except FileNotFoundError:
        print(f"오류: 입력 파일 '{input_filepath}'을(를) 찾을 수 없습니다. 경로를 확인하세요.")
    except Exception as e:
        print(f"파일 처리 중 오류 발생: {e}")

# --- 사용 방법 (아래 경로를 당신의 실제 파일 경로로 수정해주세요) ---

# 로컬 프로젝트 루트 경로 (VS Code에서 해당 파일이 있는 폴더 경로)
# 예: r"C:\Users\JHSHIN\ProgrammingCodes\deep-learning"
project_root = r"C:\Users\JHSHIN\ProgrammingCodes\deep-learning" 

# 원본 입력 파일 경로 (당신이 가지고 있는 원본 dataset.txt 파일)
input_file = os.path.join(project_root, 'dataset.txt') 

# 수정된 내용을 저장할 새로운 출력 파일 경로 (새로운 이름으로 저장하는 것을 권장)
output_file = os.path.join(project_root, 'dataset_cleaned.txt') # 파일 이름 변경

# 함수 실행
clean_and_prepare_text_for_doccano_final_v2(input_file, output_file)
import re
import json
import os

def create_weak_labels_advanced(input_text_path, output_jsonl_path):
    """
    고도로 상세화된 정규식 휴리스틱을 사용해 자동으로 라벨을 생성합니다.
    - ID, QUESTION_CONTENT, ANSWER_CONTENT는 구조 기반으로 라벨링
    - LAW_CONTENT는 상세화된 복합 패턴을 적용하여 정교하게 라벨링
    """
    try:
        with open(input_text_path, 'r', encoding='utf-8') as f:
            documents = f.read().strip().split('\n\n')
    except FileNotFoundError:
        print(f"오류: '{input_text_path}' 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return

    # --- 라벨링 규칙(패턴) 상세화 ---
    # ID 패턴
    question_id_pattern = re.compile(r'질의\s*\d+\.?(?=\s|$)')
    answer_id_pattern = re.compile(r'회신\s*\d+\.?(?=\s|$)')
    
    # LAW_CONTENT를 찾기 위한 고도로 상세화된 휴리스틱(Heuristics) 패턴
    # 우선순위가 높은(더 구체적인) 패턴을 리스트의 위쪽에 배치합니다.
    law_patterns = [
        # 1. 「...법」, 『...기준』 등 특수기호로 감싸진 법률/기준 이름 (가장 강력한 패턴)
        re.compile(r'(?:「|『)[^」』]+(?:법|법률|시행령|시행규칙|기준)(?:」|』)'),
        
        # 2. '소방시설법 시행령 제12조제1항제1호' 와 같이 법 이름과 조항이 함께 나오는 패턴
        re.compile(r'[^」』\s]+(?:법|령|규칙|기준)\s?제\s?\d+조(?:\s?제\s?\d+항)?(?:\s?제\s?\d+호)?'),
        
        # 3. '[소방시설법 제9조]' 와 같이 대괄호로 감싸진 법률 및 조항
        re.compile(r'\[\s?[^\]]+(?:법|령|기준|조)\s?[^\]]*\]'),

        # 4. '[별표5]' 와 같이 별표/서식을 나타내는 패턴
        re.compile(r'\[\s?별표\s?\d+\s?\]'),
        
        # 5. '제N조 제N항 제N호' 등 법률 조항만 단독으로 나오는 패턴
        re.compile(r'제\s?\d+조(?:\s?제\s?\d+항)?(?:\s?제\s?\d+호)?'),
        
        # 6. '화재안전기준' 등 단독으로 쓰이는 핵심 법규/기준 키워드
        re.compile(r'화재안전기준'),
        
        # 7. '...법에 따라' 등 법적 근거를 제시하는 표현 (가장 범위가 넓으므로 마지막에 배치)
        re.compile(r'\S+법[에\s](?:따라|따르면|의하면|근거하여)')
    ]

    all_labeled_docs = []
    print(f"총 {len(documents)}개의 문서에 대해 향상된 약 지도 학습을 시작합니다...")

    for doc_text in documents:
        if not doc_text.strip():
            continue

        spans = []
        markers = []

        # 1. 문서 내 모든 ID 마커의 위치와 종류를 찾음
        for match in question_id_pattern.finditer(doc_text):
            markers.append({'start': match.start(), 'end': match.end(), 'type': 'QUESTION_ID'})
        for match in answer_id_pattern.finditer(doc_text):
            markers.append({'start': match.start(), 'end': match.end(), 'type': 'ANSWER_ID'})
        
        markers.sort(key=lambda x: x['start'])
        if not markers:
            continue

        # 2. 마커를 기준으로 잘라가며 CONTENT 라벨링
        for i in range(len(markers)):
            current_marker = markers[i]
            spans.append([current_marker['start'], current_marker['end'], current_marker['type']])

            content_start = current_marker['end']
            content_end = markers[i+1]['start'] if i + 1 < len(markers) else len(doc_text)
            
            content_text_segment = doc_text[content_start:content_end]
            lstrip_len = len(content_text_segment) - len(content_text_segment.lstrip())
            content_start += lstrip_len
            content_end -= (len(content_text_segment) - len(content_text_segment.rstrip()))
            
            if content_start >= content_end: continue
            
            if current_marker['type'] == 'QUESTION_ID':
                spans.append([content_start, content_end, 'QUESTION_CONTENT'])
            
            elif current_marker['type'] == 'ANSWER_ID':
                answer_block_text = doc_text[content_start:content_end]
                law_spans_in_block = []

                # 3. ANSWER_CONTENT 내에서 모든 LAW_CONTENT 패턴 찾기
                for pattern in law_patterns:
                    for match in pattern.finditer(answer_block_text):
                        law_start = content_start + match.start()
                        law_end = content_start + match.end()
                        law_spans_in_block.append([law_start, law_end, 'LAW_CONTENT'])
                
                if not law_spans_in_block:
                    spans.append([content_start, content_end, 'ANSWER_CONTENT'])
                    continue

                # 4. 찾은 LAW_CONTENT들을 병합하고, 그 외 부분을 ANSWER_CONTENT로 라벨링
                law_spans_in_block.sort(key=lambda x: x[0])
                
                # 중첩/겹치는 부분을 병합 (Merge overlapping spans)
                merged_law_spans = []
                if law_spans_in_block:
                    current_span = law_spans_in_block[0]
                    for next_span in law_spans_in_block[1:]:
                        if next_span[0] < current_span[1]: # 겹치는 경우
                            current_span[1] = max(current_span[1], next_span[1])
                        else:
                            merged_law_spans.append(current_span)
                            current_span = next_span
                    merged_law_spans.append(current_span)

                # LAW_CONTENT를 제외한 나머지 부분을 ANSWER_CONTENT로 채우기
                last_end = content_start
                for law_start, law_end, law_label in merged_law_spans:
                    if law_start > last_end:
                        spans.append([last_end, law_start, 'ANSWER_CONTENT'])
                    spans.append([law_start, law_end, law_label])
                    last_end = law_end
                
                if content_end > last_end:
                    spans.append([last_end, content_end, 'ANSWER_CONTENT'])

        spans.sort(key=lambda x: x[0])
        all_labeled_docs.append({"text": doc_text, "labels": spans})

    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        for doc in all_labeled_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')

    print(f"고도로 상세화된 약 지도 학습 완료! {len(all_labeled_docs)}개의 문서가 '{output_jsonl_path}'에 저장되었습니다.")

# --- 함수 실행 ---
# # 아래 경로들은 실제 환경에 맞게 설정해야 합니다.
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"프로젝트 루트 경로: {project_root}")

after_perprocessing = os.path.join('data_dir', 'dataset_cleaned.txt')
weakly_labeled_path = os.path.join('data_dir', 'weakly_labeled_advanced.jsonl')
# weakly_labeled_path = os.path.join('data_dir', 'weakly_labeled_advanced.json')

# # 파일이 존재할 때만 실행
if os.path.exists(after_perprocessing):
    create_weak_labels_advanced(after_perprocessing, weakly_labeled_path)
else:
    print(f"입력 파일 '{after_perprocessing}'를 찾을 수 없어 실행을 건너뜁니다.")
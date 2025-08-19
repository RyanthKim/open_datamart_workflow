# 필요 패키지 리스트 생성 : pip freeze > resource/requirements.txt
# 필요 패키지 설치 : pip install -r resource/requirements.txt
# 
# git add .
# git commit -m "feat(): 변경사항 상세 서술"
# git push

from resource import custom_functions as func
import workflow_list as wl
import time
import requests

# 슬랙 메시지용 헤더
url = 'SLACK API URL'
headers = {'Content-type': 'application/json'}

# 팀 데이터 채널에 시작 알림
response = requests.post(
    url=url, 
    headers=headers, 
    json={"text": "<CC 그룹ID> - 데일리 테이블 업데이트 시작"}
)

# 동작부
# 시트 이름이나 쿼리 번호 등은 workflow_list.py 에서 확인

# 자유청구서 카테고리 시트에서 redshift 로 업로드 하는 부분
print(':::::::::자유청구서 카테고리 업데이트:::::::::')
for i in wl.sheet_update_list:
    sheet_id=i['sheet_id']
    sheet_name=i['sheet_name']
    table_name=i['table_name']
    print(f'- {sheet_name} 실행')
    func.db_manager.full_renew_sheet_to_redshift(sheet_id=sheet_id,sheet_name=sheet_name,table_name=table_name) # 매일

# 데일리로 돌아야 하는 쿼리 리스트 순차적으로 실행하는 부분
print(':::::::::[ 리대시 ] 테이블 업데이트 쿼리 실행:::::::::')
for query_number in wl.redash_query_number_list:
    print(f'- {query_number} 실행')
    start_time = time.time()
    
    try:
        result = func.redash_manager.get_refresh_query_result(query_number)
        print(f'\t - 결과 : {result}')
    except Exception as e:
        print(f'\t - 에러 발생: {e}')
    
    end_time = time.time()
    print(f'\t - 소요 시간: [{end_time - start_time:.6f} seconds]')

# 문서 카테고리 형태소 분석 실행하여 redshift 로 업로드 하는 부분
print(':::::::::문서 타이틀 형태소 분석 후 카테고리 업데이트:::::::::')
func.text_mining_case1.text_mining_title(
    sql=wl.document_title_mining_value["sql"],
    table_name=wl.document_title_mining_value["table_name"],
    column_names=wl.document_title_mining_value["column_names"],
    process_type=wl.document_title_mining_value["process_type"],
    delete_table=wl.document_title_mining_value["delete_table"],
    category1_file_path=wl.document_title_mining_value["json_file_path_category1"],
    category2_file_path=wl.document_title_mining_value["json_file_path_category2"],
    user_dic_path=wl.document_title_mining_value["dic_file_path"]
    )

# 템플릿 카테고리 형태소 분석 실행하여 redshift 로 업로드 하는 부분
print(':::::::::템플릿 타이틀 형태소 분석 후 카테고리 업데이트:::::::::')
func.text_mining_case1.text_mining_title(
    sql=wl.template_title_mining_value["sql"],
    table_name=wl.template_title_mining_value["table_name"],
    column_names=wl.template_title_mining_value["column_names"],
    process_type=wl.template_title_mining_value["process_type"],
    delete_table=wl.template_title_mining_value["delete_table"],
    category1_file_path=wl.template_title_mining_value["json_file_path_category1"],
    category2_file_path=wl.template_title_mining_value["json_file_path_category2"],
    user_dic_path=wl.template_title_mining_value["dic_file_path"]
    )

# 문서 서식 카테고리 형태소 분석 실행하여 redshift 로 업로드 하는 부분
print(':::::::::문서 타이틀 형태소 분석 후 서식 카테고리 업데이트:::::::::')
func.text_mining_case2.text_mining_title(
    sql=wl.document_title_to_form_mining_value["sql"],
    table_name=wl.document_title_to_form_mining_value["table_name"],
    column_names=wl.document_title_to_form_mining_value["column_names"],
    process_type=wl.document_title_to_form_mining_value["process_type"],
    delete_table=wl.document_title_to_form_mining_value["delete_table"],
    category_file_path=wl.document_title_to_form_mining_value["json_file_path"],
    user_dic_path=wl.document_title_to_form_mining_value["dic_file_path"]
    )

# 템플릿 서식 카테고리 형태소 분석 실행하여 redshift 로 업로드 하는 부분
print(':::::::::템플릿 타이틀 형태소 분석 후 서식 카테고리 업데이트:::::::::')
func.text_mining_case2.text_mining_title(
    sql=wl.template_title_to_form_mining_value["sql"],
    table_name=wl.template_title_to_form_mining_value["table_name"],
    column_names=wl.template_title_to_form_mining_value["column_names"],
    process_type=wl.template_title_to_form_mining_value["process_type"],
    delete_table=wl.template_title_to_form_mining_value["delete_table"],
    category_file_path=wl.template_title_to_form_mining_value["json_file_path"],
    user_dic_path=wl.template_title_to_form_mining_value["dic_file_path"]
    )


# 팀 데이터 채널에 종료 알림
response = requests.post(
    url = url, 
    headers=headers, 
    json={"text": "<CC 그룹ID> - 데일리 테이블 업데이트 완료"}
)


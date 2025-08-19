from konlpy.tag import Komoran
import gspread
from sqlalchemy import create_engine
import pandas as pd
import datetime
import requests
import time
import json

class DB_Manager:
    def __init__(self, id, pw, host, port, dbname):
        self.db_url = f'postgresql+psycopg2://{id}:{pw}@{host}:{port}/{dbname}'
        self.engine = create_engine(self.db_url, connect_args={"options": ""})

    @staticmethod
    def timestamp():
        return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def execute_sql(self, sql, sql_file=False):
        if sql_file:
            print(f' - DB 조회 시작 : {self.timestamp()} - {sql}')
        else:
            print(f' - DB 조회 시작 : {self.timestamp()}')
        result = pd.DataFrame()
        if sql_file:
            with open(f'update_sql_list/{sql}', 'r', encoding='utf-8') as file:
                sql = file.read().strip()
        try:
            result = pd.read_sql(sql=sql, con=self.engine)
        except Exception as error:
            print("Error: %s" % error)
        print(f'\t DB 조회 완료 : {self.timestamp()}')
        return result

    def append_data(self, rawdata, table_name):
        df = pd.DataFrame(rawdata)
        df.columns = df.columns.str.lower()
        print(f'\r - DB dump 시작 : {self.timestamp()} - {table_name} - [{len(df)} rows]')
        with self.engine.connect() as conn:
            exists = conn.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name=%s);",
                [table_name]
            ).scalar()
        message = f"\t table : {table_name} 신규테이블 입니다." if not exists else f"\t table : {table_name} 이미 존재 하여 데이터를 추가합니다."
        print(message)
        try:
            df.to_sql(name=table_name, con=self.engine, if_exists='append', chunksize=10000, index=False, method='multi')
        except Exception as error:
            print("Error: %s" % error)
        print(f'\t DB dump 완료 : {self.timestamp()}')

    def get_sheet(self, id, sheetName):
        print(f' - 시트 조회 시작 : {sheetName}')
        gc = gspread.service_account(filename='resource/project-gsheet-input-cf916fb9860d.json')
        gsheet = gc.open_by_url(f"https://docs.google.com/spreadsheets/d/{id}")
        wsheet = gsheet.worksheet(sheetName)
        temp = wsheet.get()
        result = pd.DataFrame(temp[1:],columns=temp[0])
        result.columns = result.columns.str.lower()
        print('\t 시트 조회 완료')
        return result

    def full_renew_sheet_to_redshift(self, sheet_id, sheet_name, table_name):
        result = self.get_sheet(sheet_id, sheet_name)
        self.execute_sql(f'delete from {table_name}; select 1;', sql_file=False)
        self.append_data(result, table_name=table_name)

class Redash_Manager:
    def __init__(self, api_key):
        self.url = 'https://redash.modusign.co.kr'
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'{api_key}',
            "Content-Type": 'application/json'
        })
        
    def poll_job(self, s, job):
        # TODO: add timeout
        while job['status'] not in (3, 4):
            job_id = job['id']
            response = s.get(f'{self.url}/api/jobs/{job_id}')
            job = response.json()['job']
            time.sleep(1)

        if job['status'] == 3:
            return job['query_result_id']
        
        return None

    def get_refresh_query_result(self, query_id):
        s = self.session
        response = s.post(f'{self.url}/api/queries/{query_id}/refresh')

        if response.status_code != 200:
            raise Exception('Refresh failed.')
        result_id = self.poll_job(s, response.json()['job'])
        
        if result_id:
            response = s.get(f'{self.url}/api/queries/{query_id}/results/{result_id}.json')
            if response.status_code != 200:
                raise Exception('Failed getting results.')
        else:
            raise Exception('Query execution failed.')

        return response.json()['query_result']['data']['rows']
    
    def get_cached_query_result(self, query_id):
        s = self.session
        response = s.get(f'{self.url}/api/queries/{query_id}/results')
        return response.json()['query_result']['data']['rows']

# 문서 카테고리
class Text_Mining_Algorithm_Case1:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    @staticmethod
    def open_json(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data

    def process_data(self, data, process_type, category1_file_path, category2_file_path, user_dic_path):
        try:
            h = 1
            komoran = Komoran(userdic=user_dic_path)

            dic_category_1 = self.open_json(category1_file_path)
            dic_category_2 = self.open_json(category2_file_path)

            # 형태소 매칭하는 부분
            processed_data = []
            for _, row_data in data.iterrows():
                try:
                    para = str(row_data['title']).strip().encode('utf-8', 'ignore').decode('utf-8')
                    ex_nouns = komoran.nouns(para)
                    j = '기타'
                    k = '기타'
                    for noun in ex_nouns:
                        if noun in dic_category_1:
                            j = dic_category_1[noun]
                            k = dic_category_2[noun]
                            break
                    category1 = j
                    category2 = k
                except Exception as e:
                    ex_nouns = ''
                    category1 = '기타'
                    category2 = '기타'
                    
                if process_type == 'document':
                    processed_data.append([
                        row_data['documentid'], row_data['userid'], row_data['workspaceid'], row_data['estimated_workspaceid'], row_data['createdat'],
                        str(ex_nouns), category1, category2
                    ])
                if process_type == 'template':
                    processed_data.append([
                        row_data['templateid'], row_data['workspaceid'], row_data['memberid'], row_data['title'], row_data['createdat'], str(ex_nouns), category1, category2
                    ])
                print(f'\r       - {h}', '진행중', end='')
                h += 1

            return processed_data
        except Exception as e:
            raise Exception(f"Error processing data: {e}")

    def text_mining_title(self, sql, table_name, column_names, process_type, category1_file_path, category2_file_path, user_dic_path, delete_table=False):
        try:
            if delete_table:
                try:
                    self.db_manager.execute_sql(f'delete from {table_name}')
                except Exception as e:
                    raise Exception(f"Error executing delete SQL: {e}")
            
            try:
                result = self.db_manager.execute_sql(sql)
            except Exception as e:
                raise Exception(f"Error executing SQL: {e}")
            
            batch_size = 100000
            total_rows = len(result)
            num_batches = (total_rows + batch_size - 1) // batch_size
            for i in range(num_batches):
                print(f'- {i + 1} / {num_batches} 번째')
                start_index = i * batch_size
                end_index = min((i + 1) * batch_size, total_rows)
                batch_data = result[start_index:end_index]
                
                try:
                    processed_data = self.process_data(batch_data, process_type, category1_file_path, category2_file_path, user_dic_path)
                except Exception as e:
                    raise Exception(f"Error in processing data batch {i + 1}: {e}")
                
                df = pd.DataFrame(processed_data, columns=column_names)
                self.db_manager.append_data(rawdata=df, table_name=table_name)
            print('끝')
        
        except Exception as e:
            raise Exception(f"Error in text_mining_title: {e}")

# 문서 서식 카테고리
class Text_Mining_Algorithm_Case2:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    @staticmethod
    def open_json(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data

    def process_data(self, data, process_type, category_file_path, user_dic_path):
        try:
            h = 1
            komoran = Komoran(userdic=user_dic_path)
            
            dic_category_1 = self.open_json(category_file_path)

            # 형태소 매칭하는 부분
            processed_data = []
            for _, row_data in data.iterrows():
                try:
                    para = str(row_data['title']).strip().encode('utf-8', 'ignore').decode('utf-8')
                    ex_nouns = komoran.nouns(para)
                    j = '기타'
                    for noun in ex_nouns:
                        if noun in dic_category_1:
                            j = dic_category_1[noun]
                            break
                    category1 = j
                except Exception as e:
                    ex_nouns = ''
                    category1 = '기타'
                    
                if process_type == 'document':
                    processed_data.append([
                        row_data['documentid'], row_data['userid'], row_data['workspaceid'], row_data['estimated_workspaceid'], row_data['createdat'],
                        str(ex_nouns), category1
                    ])
                if process_type == 'template':
                    processed_data.append([
                        row_data['templateid'], row_data['workspaceid'], row_data['memberid'], row_data['title'], row_data['createdat'], str(ex_nouns), category1
                    ])
                print(f'\r       - {h}', '진행중', end='')
                h += 1

            return processed_data
        except Exception as e:
            raise Exception(f"Error processing data: {e}")

    def text_mining_title(self, sql, table_name, column_names, process_type, category_file_path, user_dic_path, delete_table=False):
        try:
            if delete_table:
                self.db_manager.execute_sql(f'delete from {table_name}')
            
            try:
                result = self.db_manager.execute_sql(sql)
            except Exception as e:
                raise Exception(f"Error executing SQL: {e}")
            
            batch_size = 100000
            total_rows = len(result)
            num_batches = (total_rows + batch_size - 1) // batch_size
            for i in range(num_batches):
                print(f'- {i + 1} / {num_batches} 번째')
                start_index = i * batch_size
                end_index = min((i + 1) * batch_size, total_rows)
                batch_data = result[start_index:end_index]
                
                try:
                    processed_data = self.process_data(batch_data, process_type, category_file_path, user_dic_path)
                except Exception as e:
                    raise Exception(f"Error in processing data batch {i + 1}: {e}")
                
                df = pd.DataFrame(processed_data, columns=column_names)
                self.db_manager.append_data(rawdata=df, table_name=table_name)
            print('끝')
        
        except Exception as e:
            raise Exception(f"Error in text_mining_title: {e}")



id = 'ID'
pw = 'PASS WORD'
host = 'HOST'
port = 'PORT'
dbname = 'DBNAME'
db_manager = DB_Manager(id, pw, host, port, dbname)
text_mining_case1 = Text_Mining_Algorithm_Case1(db_manager)
text_mining_case2 = Text_Mining_Algorithm_Case2(db_manager)
redash_manager = Redash_Manager('Redash API KEY')

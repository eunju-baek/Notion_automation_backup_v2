import requests
import json
import os
from datetime import date, datetime

# 현재 날짜 정보
today = date.today()
current_year = today.year
current_month = today.month

# 해당 월의 첫날과 마지막 날 계산
first_day = date(current_year, current_month, 1)
if current_month == 12:
    last_day = date(current_year + 1, 1, 1)
else:
    last_day = date(current_year, current_month + 1, 1)

print(f"Querying data from {first_day} to {last_day}")


# Notion API 설정
headers = {
    'Authorization': 'Bearer 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',  # 실제 Notion API 토큰 입력
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'  # Notion API 버전
}

database_id = '134d13da8dfa80a29232e955d7482ade'  # 실제 데이터베이스 ID 입력
downloads_dir = os.path.join(os.getcwd(), f'downloads_{current_year}_{current_month:02d}')
os.makedirs(downloads_dir, exist_ok=True)
print(f"Downloads directory created at: {downloads_dir}")



# 데이터베이스 쿼리 함수
def query_database():
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    response = requests.post(url, headers=headers, json={}, verify=False)  # POST 요청으로 쿼리 실행
    if response.status_code != 200:
        print(f"Error querying database: {response.status_code}")
        print(response.text)
        return None
    return response.json()

# def download_file(file_url, file_name):
#     # 다운로드 디렉토리가 없으면 생성
#     if not os.path.exists(download_dir):
#         os.makedirs(download_dir)

def download_file(file_url, file_name):
    # 파일 경로 생성 (상대 경로 사용)
    file_path = os.path.join(downloads_dir, file_name)

    response = requests.get(file_url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"파일 다운로드 완료: {file_path}")
    else:
        print(f"파일 다운로드 실패: {file_name}")


    
    # 파일 경로 생성
    file_path = os.path.join(download_dir, file_name)

    response = requests.get(file_url)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"파일 다운로드 완료: {file_name}")
    else:
        print(f"파일 다운로드 실패: {file_name}")


# 결과 확인
data = query_database()
if data:
    print(json.dumps(data, indent=4))  # 데이터를 보기 좋게 출력

# 데이터베이스 쿼리 결과에서 파일 정보 추출 및 다운로드
for page in data.get('results', []):
    properties = page.get('properties', {})
    attachments = properties.get('첨부파일', {}).get('files', [])
    
    for attachment in attachments:
        file_url = attachment.get('file', {}).get('url')
        file_name = attachment.get('name')
        
        if file_url and file_name:
            download_file(file_url, file_name)

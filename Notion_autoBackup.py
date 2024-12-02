import requests
import os
import json
import pandas as pd
from datetime import datetime

# Notion API 설정
headers = {
    'Authorization': 'Bearer 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',  # 여기에 실제 Notion API 토큰 입력
    'Notion-Version': '2022-06-28',
}

# 데이터베이스 쿼리
database_id = '134d13da8dfa80a29232e955d7482ade'
url = f'https://api.notion.com/v1/databases/{database_id}/query'
response = requests.post(url, headers=headers)
if response.status_code != 200:
    print(f"Error: API request failed with status code {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

data = response.json()
if 'results' not in data:
    print("Error: 'results' key not found in API response")
    print(f"Response: {data}")
    exit(1)

    
# 데이터 처리 및 파일 다운로드
data_list = []  # CSV에 저장할 데이터 리스트

# 다운로드할 파일을 저장할 디렉토리 생성
os.makedirs('downloads', exist_ok=True)

for page in data['results']:
    page_id = page['id']
    
    # 페이지 이름 및 파일 정보 추출
    name = page['properties']['Name']['title'][0]['text']['content']
    
    # 페이지의 각 속성 추출 (예: Tags, 완료 상태 등)
    tags = [tag['name'] for tag in page['properties'].get('Tags', {}).get('multi_select', [])]
    completed = page['properties'].get('완료', {}).get('checkbox', False)
    
    # 파일 다운로드 및 정보 저장
if 'Files' in page['properties']:
    print(f"Files found in page: {page['properties']['Files']}")
    for file in page['properties']['Files']['files']:
        file_url = file['file']['url']
        file_name = file['name']
        print(f"Downloading file: {file_name} from {file_url}")
        file_response = requests.get(file_url)
        file_path = os.path.join('downloads', file_name)
        print(f"Saving file to: {file_path}")
        with open(file_path, 'wb') as f:
            f.write(file_response.content)
        print(f"File saved: {file_path}")
else:
    print(f"No files found in page: {page['id']}")

    # 데이터 리스트에 추가 (엑셀에 저장할 데이터)
    data_list.append({
        'Name': name,
        'Tags': ', '.join(tags),  # 태그를 문자열로 변환
        '완료': completed,
        '파일과 미디어': ', '.join([file['name'] for file in page['properties'].get('Files', {}).get('files', [])]),
        'Date': page['properties'].get('Date', {}).get('date', None),
    })

# 현재 날짜를 YYYYMMDD 형식으로 가져오기
current_date = datetime.now().strftime("%Y%m%d")
output_excel = f'{current_date}_DBbackup.xlsx'

# DataFrame 생성 후 엑셀로 저장
if data_list:  # 데이터가 있을 경우에만 엑셀로 저장
    df = pd.DataFrame(data_list)
    df.to_excel(output_excel, index=False)  # 엑셀 파일로 저장
    print(f"엑셀 파일이 '{output_excel}'로 저장되었습니다.")
else:
    print("No valid data found to convert.")

print("Backup complete.")

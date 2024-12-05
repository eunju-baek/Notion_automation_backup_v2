import requests
import os
import json
import pandas as pd
from datetime import date, datetime

# Notion API 설정
headers = {
    'Authorization': 'Bearer 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',  # 여기에 실제 Notion API 토큰 입력
    'Notion-Version': '2022-06-28',
}

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

# Notion API 쿼리 (날짜 필터 추가)
query = {
    "filter": {
        "and": [
            {
                "property": "Date",
                "date": {
                    "on_or_after": first_day.isoformat()
                }
            },
            {
                "property": "Date",
                "date": {
                    "before": last_day.isoformat()
                }
            }
        ]
    }
}

# 데이터베이스 쿼리
database_id = '134d13da8dfa80a29232e955d7482ade'  # 여기에 실제 데이터베이스 ID 입력
url = f'https://api.notion.com/v1/databases/{database_id}/query'
response = requests.post(url, headers=headers, json=query)

if response.status_code != 200:
    print(f"Error: API request failed with status code {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)

print(f"API Response Status: {response.status_code}")
data = response.json()
print(json.dumps(data, indent=4))  # API 응답 구조 출력

if 'results' not in data:
    print("Error: 'results' key not found in API response")
    print(f"Response: {data}")
    exit(1)

# 데이터 처리 및 파일 다운로드
data_list = []  # CSV에 저장할 데이터 리스트

# 다운로드할 파일을 저장할 디렉토리 생성
downloads_dir = os.path.join(os.getcwd(), f'downloads_{current_year}_{current_month:02d}')
os.makedirs(downloads_dir, exist_ok=True)
print(f"Downloads directory created at: {downloads_dir}")

# 엑셀 파일을 저장할 디렉토리 생성
excel_dir = os.path.join(os.getcwd(), 'excel_backups')
os.makedirs(excel_dir, exist_ok=True)

# .gitkeep 파일 생성
with open(os.path.join(downloads_dir, '.gitkeep'), 'w') as f:
    pass
print(".gitkeep file created in downloads directory")

for page in data['results']:
    page_id = page['id']
    
    # 페이지 이름 및 파일 정보 추출
    name = page['properties']['Name']['title'][0]['text']['content'] if page['properties']['Name']['title'] else 'Untitled'
    
    # 페이지의 각 속성 추출 (예: Tags, 완료 상태 등)
    tags = [tag['name'] for tag in page['properties'].get('Tags', {}).get('multi_select', [])]
    completed = page['properties'].get('완료', {}).get('checkbox', False)
    
    print(f"Processing page: {name} (ID: {page_id})")
    print(f"Page properties: {json.dumps(page['properties'], indent=2)}")

    # 파일 다운로드 및 정보 저장
    file_names = []
    if 'Files' in page['properties']:
        print(f"Files property found in page {page_id}")
        print(json.dumps(page['properties']['Files'], indent=2))
        for file in page['properties']['Files']['files']:
            file_url = file.get('file', {}).get('url') or file.get('external', {}).get('url')
            file_name = file['name']
            if file_url:
                try:
                    file_response = requests.get(file_url)
                    file_response.raise_for_status()
                    file_path = os.path.join(downloads_dir, file_name)
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                    file_names.append(file_name)
                    print(f"Successfully downloaded: {file_path}")
                except Exception as e:
                    print(f"Error downloading {file_name}: {str(e)}")
                    print(f"File URL: {file_url}")
            else:
                print(f"No URL found for file: {file_name}")
    else:
        print(f"No Files property found in page {page_id}")

    # 데이터 리스트에 추가 (엑셀에 저장할 데이터)
    data_list.append({
        'Name': name,
        'Tags': ', '.join(tags),  # 태그를 문자열로 변환
        '완료': completed,
        '파일과 미디어': ', '.join(file_names),
        'Date': page['properties'].get('Date', {}).get('date', {}).get('start', None),
    })

# 스크립트 끝에 다음 로그 추가
print(f"Contents of downloads directory:")
print(os.listdir(downloads_dir))

# 현재 날짜를 YYYYMMDD 형식으로 가져오기
current_date = datetime.now().strftime("%Y%m%d")
output_excel = os.path.join(excel_dir, f'{current_year}_{current_month:02d}_DBbackup.xlsx')

# DataFrame 생성 후 엑셀로 저장
if data_list:  # 데이터가 있을 경우에만 엑셀로 저장
    df = pd.DataFrame(data_list)
    df.to_excel(output_excel, index=False)  # 엑셀 파일로 저장
    print(f"엑셀 파일이 '{output_excel}'로 저장되었습니다.")
else:
    print("No valid data found to convert.")

print("Backup complete.")

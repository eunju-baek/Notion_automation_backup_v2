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
print(f"API Response Status: {response.status_code}")
print(f"API Response Content: {response.text[:500]}...")  # 처음 500자만 출력

data = response.json()
if 'results' not in data:
    print("Error: 'results' key not found in API response")
    print(f"Response: {data}")
    exit(1)

    
# 데이터 처리 및 파일 다운로드
data_list = []  # CSV에 저장할 데이터 리스트

# 다운로드할 파일을 저장할 디렉토리 생성
downloads_dir = os.path.join(os.getcwd(), 'downloads')
os.makedirs(downloads_dir, exist_ok=True)
print(f"Downloads directory created at: {downloads_dir}")

for page in data['results']:
    page_id = page['id']
    
    # 페이지 이름 및 파일 정보 추출
    name = page['properties']['Name']['title'][0]['text']['content']
    
    # 페이지의 각 속성 추출 (예: Tags, 완료 상태 등)
    tags = [tag['name'] for tag in page['properties'].get('Tags', {}).get('multi_select', [])]
    completed = page['properties'].get('완료', {}).get('checkbox', False)
    
    # 파일 다운로드 및 정보 저장
if 'Files' in page['properties']:
    print(f"Files found in page: {page['id']}")
    for file in page['properties']['Files']['files']:
        file_url = file['file']['url']
        file_name = file['name']
        print(f"Attempting to download: {file_name} from {file_url}")
        try:
            file_response = requests.get(file_url)
            file_response.raise_for_status()  # 오류 발생 시 예외를 발생시킵니다
            file_path = os.path.join(downloads_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_response.content)
            print(f"Successfully downloaded: {file_path}")
        except Exception as e:
            print(f"Error downloading {file_name}: {str(e)}")
else:
    print(f"No files found in page: {page['id']}")

# 스크립트 끝에 다음 로그 추가
print(f"Contents of downloads directory:")
print(os.listdir(downloads_dir))

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

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# 인증 정보
cert_key = 'd1101c1f-578b-4e60-a787-4b5dc49a63b0'
cert_id = '4781'

# KAMIS API 엔드포인트
url_daily_price = "http://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList"

# 요청 변수 설정
product_cls_code = '01'  # 구분 (02:도매, 01:소매)
item_category_code_list = ['300', '400', '600']  # 각 부류 코드
country_code = '1101'  # 지역코드 (1101: 서울)
convert_kg_yn = 'Y'  # kg단위 환산 여부

# 시작 및 종료 날짜 설정
start_year = 1996
end_year = 2023
end_date = datetime(end_year, 12, 31)

# 품목별로 데이터를 수집
for item_category_code in item_category_code_list:
    print(f"부류 {item_category_code}에 대한 데이터 수집을 시작합니다.")
    
    # 연도별로 데이터를 저장하기 위한 리스트 초기화
    for year in range(start_year, end_year + 1):
        start_date = datetime(year, 1, 1)
        end_of_year = datetime(year, 12, 31) if year != end_year else end_date
        current_date = start_date
        
        annual_data_list = []  # 각 연도별 데이터를 담을 리스트

        while current_date <= end_of_year:
            regday = current_date.strftime('%Y-%m-%d')
            params = {
                'p_cert_key': cert_key,
                'p_cert_id': cert_id,
                'p_returntype': 'xml',
                'p_product_cls_code': product_cls_code,
                'p_item_category_code': item_category_code,
                'p_country_code': country_code,
                'p_regday': regday,
                'p_convert_kg_yn': convert_kg_yn
            }

            print(f"Processing data for {regday}...")
            try:
                response = requests.get(url_daily_price, params=params, timeout=10)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    for item in root.findall('.//item'):
                        item_name = item.findtext('item_name')
                        item_code = item.findtext('item_code')
                        price = item.findtext('dpr1')

                        # 데이터가 이미 존재하는지 확인
                        if not any((d['date'] == regday and d['item_name'] == item_name) for d in annual_data_list):
                            data = {
                                'date': regday,
                                'item_name': item_name,
                                'item_code': item_code,
                                'unit': item.findtext('unit'),
                                'price': price
                            }
                            annual_data_list.append(data)
                            print(f"Added data for {item_name} on {regday}")
                else:
                    print(f"Failed to fetch data for {regday}, status code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Error: {e} for {regday}")

            current_date += timedelta(days=1)

        # 연도별 데이터 프레임 생성 및 저장
        df_annual = pd.DataFrame(annual_data_list)
        df_annual.drop_duplicates(subset=['date', 'item_name', 'item_code'], keep='first', inplace=True)

        # 파일로 저장
        if not df_annual.empty:
            file_name = f'C:/Users/SSAFY/Desktop/분석/시계열분석/축산제외 전체시계열데이터/{item_category_code}_{year}_data.xlsx'
            df_annual.to_excel(file_name, index=False)
            print(f"Saved data to {file_name} for year {year}")
        else:
            print(f"No data found for {item_category_code} in year {year}")

    print(f"부류 {item_category_code}에 대한 데이터 수집이 완료되었습니다.")

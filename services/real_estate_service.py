# real_estate_service.py

import os
import requests


# 부동산 데이터 요청 함수
def fetch_real_estate_data(region_code, start_year, end_year):
    url = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"

    # 환경 변수로부터 API 키 가져오기
    api_key = os.getenv("REAL_ESTATE_API_KEY")

    # 부동산 데이터 요청 파라미터 설정
    params = {
        "KEY": api_key,
        "STATBL_ID": "A_2024_00178",  # 서울 및 세종 아파트 매매 지수
        "DTACYCLE_CD": "MM",  # 연간 데이터 주기
        "CLS_ID": region_code,  # 지역 코드 (세종, 수도권, 전국)
        "START_WRTTIME": start_year,  # 자료 시작일
        "END_WRTTIME": end_year,  # 자료 종료일
        "ITM_ID": "100001",
        "Type": "json"  # 응답 형식 JSON
    }

    # API 요청 보내기
    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            return response.json()  # 응답 파싱
        except ValueError:  # JSONDecodeError 처리
            return {"error": "Failed to decode JSON"}
    else:
        return {"error": f"Failed to fetch data: {response.status_code}"}  # 오류 처리


# 세종, 수도권, 전국 데이터 요청 예시
def get_real_estate_data(region, start_year, end_year):
    # 지역 코드 설정
    regions = {
        "sejong": 500014,
        "capital_area": 500002,
        "nationwide": 500001
    }

    # 유효한 지역 코드 확인
    if region not in regions:
        return {"error": "Invalid region specified"}

    region_code = regions[region]

    # 해당 지역에 대한 데이터 요청
    return fetch_real_estate_data(region_code, start_year, end_year)

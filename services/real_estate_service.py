# real_estate_service.py

import os
import requests
from datetime import datetime


# 부동산 데이터 요청 함수
def fetch_real_estate_data(region_code, start_year, end_year, statbl_id):
    url = "https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do"

    # 환경 변수로부터 API 키 가져오기
    api_key = os.getenv("REAL_ESTATE_API_KEY")

    # 부동산 데이터 요청 파라미터 설정
    params = {
        "KEY": api_key,
        "STATBL_ID": statbl_id,  # 통계표 ID
        "DTACYCLE_CD": "MM",  # 월 데이터 주기
        "CLS_ID": region_code,  # 지역 코드 (세종, 수도권, 전국)
        "START_WRTTIME": start_year,  # 자료 시작일
        "END_WRTTIME": end_year,  # 자료 종료일
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


# 아파트 매매가격지수 데이터 요청
def get_real_estate_data_apartment(region):
    # 지역 코드 설정
    regions = {
        "sejong": 500016,
        "capital_area": 500002,
        "nationwide": 500001
    }

    # 아파트 매매가격지수 통계표 ID (A_2024_00045)
    statbl_id = "A_2024_00045"

    region_code = regions.get(region)
    if not region_code:
        return {"error": "Invalid region"}

    # 2017년부터 2024년까지의 데이터 요청
    start_year = 2017
    end_year = 2024

    # 부동산 데이터 요청
    data = fetch_real_estate_data(region_code, start_year, end_year, statbl_id)

    return data


# 주택 종합 매매가격지수 데이터 요청
def get_real_estate_data_housing(region):
    # 지역 코드 설정
    regions = {
        "sejong": 500016,
        "capital_area": 500002,
        "nationwide": 500001
    }

    # 주택 종합 매매가격지수 통계표 ID (A_2024_00016)
    statbl_id = "A_2024_00016"

    region_code = regions.get(region)
    if not region_code:
        return {"error": "Invalid region"}

    # 2017년부터 2024년까지의 데이터 요청
    start_year = 2017
    end_year = 2024

    # 부동산 데이터 요청
    data = fetch_real_estate_data(region_code, start_year, end_year, statbl_id)

    return data


# 날짜별 데이터 분리 함수
def split_data_by_date(data):
    before_sep = []  # 2020년 9월 이전 데이터
    after_sep = []   # 2020년 10월 이후 데이터

    for record in data.get('row', []):
        # "2017년 1월"과 같은 형식의 날짜 문자열을 "2017-01-01" 형식으로 변환
        date_str = record.get("WRTTIME_DESC")
        try:
            # "yyyy년 mm월" 형태에서 "yyyy-mm-01"로 변환
            date_obj = datetime.strptime(date_str + " 1일", "%Y년 %m월 %d일")
        except ValueError:
            continue  # 날짜 형식이 맞지 않으면 skip

        # 2020년 9월 이전 데이터와 이후 데이터로 분리
        if date_obj < datetime(2020, 10, 1):  # 2020년 9월 이전
            before_sep.append(record)
        else:  # 2020년 10월 이후
            after_sep.append(record)

    return before_sep, after_sep

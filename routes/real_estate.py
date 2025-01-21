# real_estate.py

from flask import Blueprint, jsonify, request
from services.real_estate_service import (
    get_real_estate_data_apartment,
    get_real_estate_data_housing,
    split_data_by_date
)
from services.real_estate_calculation import calculate_sequential_change

# Blueprint 생성
real_estate_bp = Blueprint('real_estate', __name__)


# 아파트 매매 가격지수 요청 엔드포인트
@real_estate_bp.route('/real-estate/apartment', methods=['GET'])
def get_apartment_data():
    region = request.args.get('region')
    data = get_real_estate_data_apartment(region)
    return jsonify(data)


# 주택 종합 매매 가격지수 요청 엔드포인트
@real_estate_bp.route('/real-estate/housing', methods=['GET'])
def get_housing_data():
    region = request.args.get('region')
    data = get_real_estate_data_housing(region)
    return jsonify(data)


# 부동산 변동률 계산 엔드포인트
@real_estate_bp.route('/real-estate/change-rate', methods=['GET'])
def calculate_change_rate():
    region = request.args.get('region')  # 예: sejong, capital_area, nationwide
    property_type = request.args.get('type', 'apartment')  # 기본값: apartment

    # 데이터 가져오기
    if property_type == 'apartment':
        raw_data = get_real_estate_data_apartment(region)
    elif property_type == 'housing':
        raw_data = get_real_estate_data_housing(region)
    else:
        return jsonify({"error": "Invalid property type. Choose 'apartment' or 'housing'."})

    # 에러 응답 처리
    if 'error' in raw_data:
        return jsonify(raw_data)

    # 필요한 데이터만 추출
    try:
        row_data = raw_data.get("SttsApiTblData", [{}])[1].get("row", [])
        if not row_data:
            return jsonify({"error": "No data available in the response."})

        # 데이터 타입 검사
        for entry in row_data:
            if not isinstance(entry, dict):
                raise ValueError(f"Invalid entry format: {entry}")
    except Exception as e:
        return jsonify({"error": f"Data extraction error: {str(e)}"})

    # 데이터 정제
    try:
        before_sep, after_sep = split_data_by_date({"row": row_data})
        combined_data = {"row": before_sep + after_sep}
        # print("DEBUG: combined_data['row']:", combined_data["row"])  # 디버깅 추가
    except Exception as e:
        return jsonify({"error": f"Data processing error: {str(e)}"})

    # 분기별 변동률 계산
    try:
        change_rate = calculate_sequential_change(combined_data)
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"})

    return jsonify({
        "region": region,
        "property_type": property_type,
        "change_rate": change_rate
    })

# real_estate.py

from flask import Blueprint, jsonify, request
from services.real_estate_service import get_real_estate_data_apartment, get_real_estate_data_housing

# Blueprint 생성
real_estate_bp = Blueprint('real_estate', __name__)


# 아파트 매매 가격지수 요청 엔드포인트
@real_estate_bp.route('/real-estate/apartment', methods=['GET'])
def get_apartment_data():
    # 요청으로부터 region 파라미터 받기
    region = request.args.get('region')

    # 아파트 매매가격지수 데이터 요청
    data = get_real_estate_data_apartment(region)

    return jsonify(data)


# 주택 종합 매매 가격지수 요청 엔드포인트
@real_estate_bp.route('/real-estate/housing', methods=['GET'])
def get_housing_data():
    # 요청으로부터 region 파라미터 받기
    region = request.args.get('region')

    # 주택 종합 매매가격지수 데이터 요청
    data = get_real_estate_data_housing(region)

    return jsonify(data)

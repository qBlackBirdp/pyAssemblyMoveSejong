# real_estate.py

from flask import Blueprint, jsonify, request
from services.real_estate_service import get_real_estate_data

# Blueprint 생성
real_estate_bp = Blueprint('real_estate', __name__)


# 부동산 데이터 요청을 위한 엔드포인트
@real_estate_bp.route('/real-estate/data', methods=['GET'])
def get_real_estate_data_endpoint():
    # 요청 파라미터 받아오기
    region = request.args.get('region', 'sejong')  # 기본값: 'sejong'
    start_year = int(request.args.get('start_year', 2017))  # 기본값: 2017
    end_year = int(request.args.get('end_year', 2024))  # 기본값: 2024

    # 데이터 요청
    data = get_real_estate_data(region, start_year, end_year)

    # 결과 반환
    return jsonify(data)

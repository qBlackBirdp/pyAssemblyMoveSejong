# real_estate.py
import requests
from flask import Blueprint, jsonify, request, render_template
from services.real_estate_service import (
    get_real_estate_data_apartment,
    get_real_estate_data_housing,
    split_data_by_date
)
from services.real_estate_calculation import calculate_sequential_change
import matplotlib.pyplot as plt
import io
import base64

# Blueprint 생성
real_estate_bp = Blueprint('real_estate', __name__)
visualization_bp = Blueprint('visualization', __name__)


# 아파트 매매 가격지수 요청 엔드포인트
@real_estate_bp.route('/apartment', methods=['GET'])
def get_apartment_data():
    region = request.args.get('region')
    data = get_real_estate_data_apartment(region)
    return jsonify(data)


# 주택 종합 매매 가격지수 요청 엔드포인트
@real_estate_bp.route('/housing', methods=['GET'])
def get_housing_data():
    region = request.args.get('region')
    data = get_real_estate_data_housing(region)
    return jsonify(data)


# 부동산 변동률 계산 엔드포인트
@real_estate_bp.route('/change-rate', methods=['GET'])
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


@visualization_bp.route('/visualize', methods=['POST'])
def visualize_change_rate():
    try:
        # 클라이언트로부터 JSON 데이터를 POST 요청으로 받음
        request_data = request.get_json()
        print("DEBUG: Received request data:", request_data)

        change_rate_data = request_data.get("change_rate", {})
        region = request_data.get("region", "Unknown").capitalize()  # region 값을 확인하고 처리

        print("DEBUG: Parsed change rate data:", change_rate_data)

        # 데이터 유효성 검사
        if not change_rate_data:
            print("DEBUG: Change rate data is missing or empty")
            return jsonify({"error": "Change rate data is missing or invalid"}), 400

        # 데이터 추출
        quarters = list(change_rate_data.keys())
        change_rates = [entry.get("Change Rate") for entry in change_rate_data.values()]
        current_avg = [entry.get("Current Avg") for entry in change_rate_data.values()]

        print("DEBUG: Quarters:", quarters)  # 디버깅 추가
        print("DEBUG: Change Rates:", change_rates)  # 디버깅 추가
        print("DEBUG: Current Averages:", current_avg)  # 디버깅 추가

        # 데이터 유효성 확인
        if not quarters or not any(change_rates) or not any(current_avg):
            print("DEBUG: Invalid or empty data for plotting")  # 디버깅 추가
            return jsonify({"error": "No valid data to visualize"}), 400

        # 변동률 그래프 생성
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(quarters, change_rates, marker='o', label='Change Rate (%)')
        ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, label='Baseline (0%)')
        ax1.set_title(f"Quarterly Change Rate (%) - {region}", fontsize=14)  # region 값 사용
        ax1.set_xlabel('Quarter', fontsize=12)
        ax1.set_ylabel('Change Rate (%)', fontsize=12)
        ax1.legend()
        ax1.grid(True)
        plt.xticks(rotation=45)

        # 이미지를 메모리 버퍼에 저장
        img1 = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img1, format='png')
        img1.seek(0)
        change_rate_img = base64.b64encode(img1.getvalue()).decode('utf8')
        plt.close(fig1)

        # 평균값 그래프 생성
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(quarters, current_avg, marker='o', color='orange', label='Average Value')
        ax2.set_title(f"Quarterly Average Values - {region}", fontsize=14)  # region 값 사용
        ax2.set_xlabel('Quarter', fontsize=12)
        ax2.set_ylabel('Average Value', fontsize=12)
        ax2.legend()
        ax2.grid(True)
        plt.xticks(rotation=45)

        # 이미지를 메모리 버퍼에 저장
        img2 = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img2, format='png')
        img2.seek(0)
        average_value_img = base64.b64encode(img2.getvalue()).decode('utf8')
        plt.close(fig2)

        # JSON 응답 생성
        return jsonify({
            "region": region,
            "change_rate_image": f"data:image/png;base64,{change_rate_img}",
            "average_value_image": f"data:image/png;base64,{average_value_img}"
        })

    except Exception as e:
        print(f"DEBUG: Visualization Error: {e}")  # 디버깅 추가
        return jsonify({"error": "Failed to generate visualization", "details": str(e)}), 500


@real_estate_bp.route('/full-visualization', methods=['GET'])
def full_visualization():
    region = request.args.get('region', 'nationwide')
    property_type = request.args.get('type', 'apartment')

    # Step 1: /change-rate 호출
    change_rate_response = requests.get(
        "http://127.0.0.1:5000/api/real-estate/change-rate",
        params={"region": region, "type": property_type}
    )

    if change_rate_response.status_code != 200:
        return jsonify({"error": "Failed to fetch change rate data"}), 500

    change_rate_data = change_rate_response.json().get('change_rate', {})

    # Step 2: /visualize 호출
    visualization_response = requests.post(
        "http://127.0.0.1:5000/api/visualization/visualize",
        json={
            "region": region,
            "change_rate": change_rate_data
        }
    )

    if visualization_response.status_code != 200:
        return jsonify({"error": "Failed to generate visualization"}), 500

    # 이미지 데이터를 템플릿에 전달하여 HTML로 렌더링
    return render_template('visualization.html',
                           change_rate_image=visualization_response.json().get('change_rate_image'),
                           average_value_image=visualization_response.json().get('average_value_image'))

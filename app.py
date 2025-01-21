from flask import Flask
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수로부터 API 키 읽어오기
api_key = os.getenv("REAL_ESTATE_API_KEY")
print(f"API Key: {api_key}")

# Flask 애플리케이션 생성
app = Flask(__name__)

# 라우트 등록
from routes.real_estate import real_estate_bp, visualization_bp

app.register_blueprint(real_estate_bp, url_prefix="/api/real-estate")
app.register_blueprint(visualization_bp, url_prefix='/api/visualization')

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True)

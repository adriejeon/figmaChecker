#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, send_file
import json
import re
import requests
import os
from datetime import datetime
from design_checker import DesignChecker
import tempfile
import zipfile
import io

app = Flask(__name__)

def extract_figma_file_key(url):
    """피그마 URL에서 파일 키를 추출"""
    # https://www.figma.com/file/XXXXX/YYYYY 형식에서 XXXXX 부분 추출
    pattern = r'figma\.com/file/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_figma_json(file_key, access_token):
    """피그마 API를 사용해서 JSON 데이터 가져오기"""
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {
        "X-Figma-Token": access_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"피그마 API 요청 실패: {str(e)}")

def save_json_to_file(data, filename):
    """JSON 데이터를 파일로 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        figma_url = request.form.get('figma_url')
        access_token = request.form.get('access_token')
        
        if not figma_url or not access_token:
            return jsonify({'error': '피그마 URL과 액세스 토큰을 모두 입력해주세요.'}), 400
        
        # 파일 키 추출
        file_key = extract_figma_file_key(figma_url)
        if not file_key:
            return jsonify({'error': '올바른 피그마 URL을 입력해주세요.'}), 400
        
        # 피그마 JSON 가져오기
        figma_data = get_figma_json(file_key, access_token)
        
        # 임시 파일로 저장
        temp_file = f"temp_figma_{file_key}.json"
        save_json_to_file(figma_data, temp_file)
        
        # 디자인 검수 실행
        checker = DesignChecker()
        design_elements = checker.extract_design_elements(temp_file)
        
        # 명세서 로드 (기본 명세서 사용)
        spec_file = "specification.json"
        if os.path.exists(spec_file):
            spec_elements = checker.load_specification_from_file(spec_file)
            checker.match_design_with_spec()
            report = checker.generate_report()
        else:
            # 기본 명세서가 없으면 디자인 요소만 분석
            report = {
                'total_elements': len(design_elements),
                'text_elements': [elem.text_content for elem in design_elements if elem.text_content.strip()],
                'timestamp': datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')
            }
        
        # 임시 파일 삭제
        os.remove(temp_file)
        
        return jsonify({
            'success': True,
            'report': report,
            'design_elements': [
                {
                    'id': elem.id,
                    'name': elem.name,
                    'text_content': elem.text_content,
                    'path': elem.path
                } for elem in design_elements
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_report', methods=['POST'])
def download_report():
    try:
        report_data = request.json
        report_html = generate_report_html(report_data)
        
        # HTML 파일로 저장
        filename = f"figma_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        return send_file(filename, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_report_html(report_data):
    """보고서 HTML 생성"""
    html_template = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>피그마 디자인 분석 보고서</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
            .section { margin: 20px 0; }
            .element { background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📝 피그마 디자인 분석 보고서</h1>
            <p>생성일시: {timestamp}</p>
        </div>
        
        <div class="section">
            <h2>📊 분석 결과</h2>
            <p>총 디자인 요소: {total_elements}개</p>
        </div>
        
        <div class="section">
            <h2>📝 텍스트 요소들</h2>
            {text_elements_html}
        </div>
    </body>
    </html>
    """
    
    text_elements_html = ""
    for elem in report_data.get('design_elements', []):
        text_elements_html += f"""
        <div class="element">
            <strong>{elem['name']}</strong><br>
            텍스트: {elem['text_content']}<br>
            경로: {elem['path']}
        </div>
        """
    
    return html_template.format(
        timestamp=report_data.get('timestamp', ''),
        total_elements=report_data.get('total_elements', 0),
        text_elements_html=text_elements_html
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

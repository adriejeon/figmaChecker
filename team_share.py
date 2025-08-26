#!/usr/bin/env python3
import os
import json
import subprocess
import socket
import webbrowser
from datetime import datetime

def get_local_ip():
    # 로컬 IP 주소 가져오기
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def create_team_share_report():
    # 팀 공유용 보고서 생성
    print("👥 팀 공유용 보고서를 생성하는 중...")
    
    # 현재 IP 주소 가져오기
    local_ip = get_local_ip()
    
    # 팀 공유용 HTML 생성
    share_html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>팀 공유 - 피그마 디자인 검수 보고서</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .content {{
            padding: 40px;
        }}
        .share-links {{
            display: grid;
            gap: 20px;
            margin: 30px 0;
        }}
        .share-link {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .share-link h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .share-link p {{
            margin: 0 0 15px 0;
            color: #666;
        }}
        .url-box {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            word-break: break-all;
            border: 1px solid #dee2e6;
        }}
        .copy-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }}
        .copy-btn:hover {{
            background: #5a6fd8;
        }}
        .instructions {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .instructions h3 {{
            margin: 0 0 15px 0;
            color: #856404;
        }}
        .instructions ol {{
            margin: 0;
            padding-left: 20px;
        }}
        .instructions li {{
            margin: 5px 0;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👥 팀 공유</h1>
            <p>피그마 디자인 검수 보고서</p>
        </div>
        
        <div class="content">
            <div class="instructions">
                <h3>📋 팀원들과 공유하는 방법</h3>
                <ol>
                    <li>아래 URL을 팀원들에게 공유하세요</li>
                    <li>팀원들은 브라우저에서 URL을 열어 보고서를 확인할 수 있습니다</li>
                    <li>실시간으로 업데이트된 검수 결과를 확인할 수 있습니다</li>
                </ol>
            </div>
            
            <div class="share-links">
                <div class="share-link">
                    <h3>🌐 로컬 접속</h3>
                    <p>같은 네트워크의 팀원들이 접속할 수 있는 URL</p>
                    <div class="url-box">http://{local_ip}:8000</div>
                    <button class="copy-btn" onclick="copyToClipboard('http://{local_ip}:8000')">URL 복사</button>
                </div>
                
                <div class="share-link">
                    <h3>📱 모바일 접속</h3>
                    <p>모바일 기기에서도 확인 가능</p>
                    <div class="url-box">http://{local_ip}:8000</div>
                    <button class="copy-btn" onclick="copyToClipboard('http://{local_ip}:8000')">URL 복사</button>
                </div>
            </div>
            
            <div class="instructions">
                <h3>⚡ 빠른 시작</h3>
                <p>터미널에서 다음 명령어를 실행하세요:</p>
                <div class="url-box">python3 run_server.py</div>
            </div>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(function() {{
                alert('URL이 클립보드에 복사되었습니다!');
            }});
        }}
    </script>
</body>
</html>'''
    
    # 팀 공유용 HTML 파일 저장
    with open("team_share.html", "w", encoding="utf-8") as f:
        f.write(share_html)
    
    print("✅ team_share.html 파일이 생성되었습니다.")
    
    # 브라우저에서 열기
    webbrowser.open(f"file://{os.path.abspath('team_share.html')}")
    
    return local_ip

if __name__ == "__main__":
    local_ip = create_team_share_report()
    print(f"🌐 팀 공유 URL: http://{local_ip}:8000")

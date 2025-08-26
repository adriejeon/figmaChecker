#!/usr/bin/env python3
import os
import json
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

class GitHubDeployer:
    def __init__(self):
        self.repo_name = "figma-design-checker"
        self.github_username = "your-username"  # GitHub 사용자명으로 변경 필요
        self.branch_name = "gh-pages"
        
    def create_github_pages_structure(self):
        """GitHub Pages용 파일 구조 생성"""
        print("📁 GitHub Pages 구조를 생성하는 중...")
        
        # gh-pages 디렉토리 생성
        gh_pages_dir = Path("gh-pages")
        gh_pages_dir.mkdir(exist_ok=True)
        
        # HTML 파일 복사
        if os.path.exists("design_text_check_report.html"):
            with open("design_text_check_report.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # GitHub Pages용 index.html 생성
            with open(gh_pages_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print("✅ index.html 파일이 생성되었습니다.")
        
        # README.md 생성
        readme_content = f"""# 피그마 디자인 검수 보고서

## 📊 검수 결과

- **생성일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
- **프로젝트**: 생성형AI캠페인
- **검수 항목**: 10개

## 🔍 검수 내용

1. **텍스트 일치도 검사** - 버튼명, 페이지명, 다이얼로그 텍스트
2. **디스크립션 구현 여부** - 설계서의 텍스트가 디자인에 구현되었는지 확인
3. **구현률 계산** - 각 항목별 텍스트 구현 비율

## 📈 결과 요약

- ✅ **완전 구현**: 모든 필요한 텍스트가 구현됨
- ⚠️ **부분 구현**: 일부 텍스트만 구현됨  
- ❌ **미구현**: 필요한 텍스트가 구현되지 않음

## 🚀 사용 방법

1. 피그마 파일에서 JSON 데이터 추출
2. 설계서 JSON 파일 준비
3. `python3 design_checker.py` 실행
4. 브라우저에서 보고서 확인

## 📁 파일 구조

```
figmaCheck/
├── design_checker.py          # 메인 검수 스크립트
├── specification.json         # 화면 설계서
├── figma_detailed.json       # 피그마 디자인 데이터
├── design_text_check_report.html  # 로컬 보고서
└── gh-pages/
    └── index.html            # GitHub Pages 보고서
```

## 🔧 기술 스택

- **Python 3.8+**
- **HTML/CSS/JavaScript**
- **Figma API**
- **GitHub Pages**

---
*자동 생성된 보고서입니다.*
"""
        
        with open(gh_pages_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print("✅ README.md 파일이 생성되었습니다.")
        
        return gh_pages_dir
    
    def create_deployment_script(self):
        """GitHub Pages 배포 스크립트 생성"""
        deploy_script = """#!/bin/bash

# GitHub Pages 배포 스크립트

echo "🚀 GitHub Pages 배포를 시작합니다..."

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"

# gh-pages 브랜치로 전환
git checkout -b gh-pages

# 기존 파일 제거 (index.html 제외)
git rm -rf . || true

# gh-pages 디렉토리의 파일들을 루트로 복사
cp -r gh-pages/* . || true

# 파일 추가
git add .

# 커밋
git commit -m "📊 피그마 디자인 검수 보고서 업데이트 - $(date)"

# 원격 저장소에 푸시
git push origin gh-pages --force

# 원래 브랜치로 돌아가기
git checkout $CURRENT_BRANCH

echo "✅ 배포가 완료되었습니다!"
echo "🌐 https://your-username.github.io/figma-design-checker 에서 확인하세요."
"""
        
        with open("deploy.sh", "w", encoding="utf-8") as f:
            f.write(deploy_script)
        
        # 실행 권한 부여
        os.chmod("deploy.sh", 0o755)
        print("✅ deploy.sh 스크립트가 생성되었습니다.")
    
    def create_github_workflow(self):
        """GitHub Actions 워크플로우 생성"""
        workflow_dir = Path(".github/workflows")
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_content = """name: Deploy Design Check Report

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
    
    - name: Run design check
      run: |
        python3 design_checker.py
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./gh-pages
"""
        
        with open(workflow_dir / "deploy.yml", "w", encoding="utf-8") as f:
            f.write(workflow_content)
        
        print("✅ GitHub Actions 워크플로우가 생성되었습니다.")
    
    def create_simple_server(self):
        """간단한 웹 서버 스크립트 생성"""
        server_script = """#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

def run_server(port=8000):
    # gh-pages 디렉토리로 이동
    gh_pages_dir = Path("gh-pages")
    if gh_pages_dir.exists():
        os.chdir(gh_pages_dir)
    
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        print(f"🌐 서버가 http://localhost:{port} 에서 실행 중입니다.")
        print("📱 팀원들과 공유할 수 있는 URL:")
        print(f"   - 로컬: http://localhost:{port}")
        print(f"   - 네트워크: http://[your-ip]:{port}")
        
        # 브라우저에서 열기
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n🛑 서버를 종료합니다.")

if __name__ == "__main__":
    run_server()
"""
        
        with open("run_server.py", "w", encoding="utf-8") as f:
            f.write(server_script)
        
        os.chmod("run_server.py", 0o755)
        print("✅ run_server.py 스크립트가 생성되었습니다.")
    
    def create_team_share_script(self):
        """팀 공유용 스크립트 생성"""
        share_script = """#!/usr/bin/env python3
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
"""
        
        with open("team_share.py", "w", encoding="utf-8") as f:
            f.write(share_script)
        
        os.chmod("team_share.py", 0o755)
        print("✅ team_share.py 스크립트가 생성되었습니다.")
    
    def deploy(self):
        """전체 배포 프로세스 실행"""
        print("🚀 GitHub Pages 배포 준비를 시작합니다...")
        
        # 1. GitHub Pages 구조 생성
        self.create_github_pages_structure()
        
        # 2. 배포 스크립트 생성
        self.create_deployment_script()
        
        # 3. GitHub Actions 워크플로우 생성
        self.create_github_workflow()
        
        # 4. 간단한 웹 서버 스크립트 생성
        self.create_simple_server()
        
        # 5. 팀 공유 스크립트 생성
        self.create_team_share_script()
        
        print("\\n🎉 배포 준비가 완료되었습니다!")
        print("\\n📋 다음 단계:")
        print("1. GitHub 저장소 생성: https://github.com/new")
        print("2. 저장소 이름: figma-design-checker")
        print("3. 터미널에서 다음 명령어 실행:")
        print("   git init")
        print("   git add .")
        print("   git commit -m 'Initial commit'")
        print("   git remote add origin https://github.com/your-username/figma-design-checker.git")
        print("   git push -u origin main")
        print("4. GitHub 저장소 설정에서 Pages 활성화")
        print("5. 팀 공유: python3 team_share.py")

def main():
    deployer = GitHubDeployer()
    deployer.deploy()

if __name__ == "__main__":
    main()

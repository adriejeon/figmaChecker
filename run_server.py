#!/usr/bin/env python3
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
            print("\n🛑 서버를 종료합니다.")

if __name__ == "__main__":
    run_server()

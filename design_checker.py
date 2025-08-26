#!/usr/bin/env python3
import json
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import webbrowser
import os

@dataclass
class DesignElement:
    id: str
    name: str
    type: str
    text_content: str
    description: str
    path: str
    properties: Dict[str, Any]

@dataclass
class SpecificationElement:
    id: str
    name: str
    text_content: str
    description: str
    category: str
    priority: str
    design_texts: List[str]

class DesignChecker:
    def __init__(self):
        self.design_elements: List[DesignElement] = []
        self.spec_elements: List[SpecificationElement] = []
        self.matches: List[Dict[str, Any]] = []
        self.issues: List[Dict[str, Any]] = []
        
    def extract_design_elements(self, json_file: str) -> List[DesignElement]:
        """피그마 JSON에서 디자인 요소들을 추출"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        elements = []
        
        def extract_text_content(node):
            """노드에서 텍스트 내용 추출"""
            text_content = ""
            if isinstance(node, dict):
                if node.get('type') == 'TEXT':
                    text_content = node.get('characters', '')
                elif 'characters' in node:
                    text_content = node.get('characters', '')
                elif 'name' in node:
                    text_content = node.get('name', '')
            return text_content
        
        def traverse_nodes(node, path=""):
            if isinstance(node, dict):
                # 텍스트 요소만 추출 (TEXT 타입)
                if node.get('type') == 'TEXT':
                    text_content = extract_text_content(node)
                    if text_content.strip():  # 빈 텍스트가 아닌 경우만
                        element = DesignElement(
                            id=node.get('id', ''),
                            name=node.get('name', ''),
                            type=node.get('type', ''),
                            text_content=text_content.strip(),
                            description=node.get('description', ''),
                            path=path,
                            properties={
                                'fills': node.get('fills', []),
                                'strokes': node.get('strokes', []),
                                'effects': node.get('effects', []),
                                'constraints': node.get('constraints', {}),
                                'layoutMode': node.get('layoutMode', ''),
                                'itemSpacing': node.get('itemSpacing', ''),
                                'paddingLeft': node.get('paddingLeft', ''),
                                'paddingRight': node.get('paddingRight', ''),
                                'paddingTop': node.get('paddingTop', ''),
                                'paddingBottom': node.get('paddingBottom', '')
                            }
                        )
                        elements.append(element)
                
                # 자식 요소들 탐색
                for key, value in node.items():
                    if isinstance(value, (dict, list)):
                        traverse_nodes(value, f"{path}.{key}" if path else key)
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    traverse_nodes(item, f"{path}[{i}]")
        
        traverse_nodes(data)
        return elements
    
    def load_specification_from_file(self, spec_file: str) -> List[SpecificationElement]:
        """설계서 파일에서 명세 요소들을 로드"""
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            specs = []
            for item in data.get('specifications', []):
                spec = SpecificationElement(
                    id=item.get('id', ''),
                    name=item.get('name', ''),
                    text_content=item.get('text_content', ''),
                    description=item.get('description', ''),
                    category=item.get('category', ''),
                    priority=item.get('priority', ''),
                    design_texts=item.get('design_texts', [])
                )
                specs.append(spec)
            return specs
        except FileNotFoundError:
            print(f"설계서 파일 {spec_file}을 찾을 수 없습니다.")
            return []
    
    def check_text_implementation(self, spec_elem: SpecificationElement, design_elements: List[DesignElement]) -> Dict[str, Any]:
        """설계서의 디자인 텍스트들이 실제 디자인에 구현되어 있는지 확인"""
        required_texts = spec_elem.design_texts
        found_texts = []
        missing_texts = []
        
        # 디자인에서 모든 텍스트 수집
        all_design_texts = [elem.text_content for elem in design_elements]
        
        for required_text in required_texts:
            found = False
            for design_text in all_design_texts:
                # 정확한 매칭 또는 포함 관계 확인
                if (required_text.lower() == design_text.lower() or 
                    required_text.lower() in design_text.lower() or 
                    design_text.lower() in required_text.lower()):
                    found_texts.append({
                        'required': required_text,
                        'found': design_text,
                        'match_type': 'exact' if required_text.lower() == design_text.lower() else 'partial'
                    })
                    found = True
                    break
            
            if not found:
                missing_texts.append(required_text)
        
        # 구현률 계산
        implementation_rate = len(found_texts) / len(required_texts) if required_texts else 0
        
        return {
            'spec_id': spec_elem.id,
            'spec_name': spec_elem.name,
            'required_texts': required_texts,
            'found_texts': found_texts,
            'missing_texts': missing_texts,
            'implementation_rate': implementation_rate,
            'status': 'complete' if implementation_rate == 1.0 else 'partial' if implementation_rate > 0 else 'missing'
        }
    
    def compare_elements(self) -> Tuple[List[Dict], List[Dict]]:
        """디자인 요소와 설계서 요소를 비교"""
        matches = []
        issues = []
        
        # 각 설계서 요소에 대해 텍스트 구현 여부 확인
        for spec_elem in self.spec_elements:
            result = self.check_text_implementation(spec_elem, self.design_elements)
            
            if result['status'] == 'complete':
                matches.append(result)
            elif result['status'] == 'partial':
                matches.append(result)
            else:
                issues.append(result)
        
        return matches, issues
    
    def generate_html_report(self, matches: List[Dict], issues: List[Dict]) -> str:
        """HTML 형태의 검수 보고서 생성"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>피그마 디자인 텍스트 검수 보고서</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 500;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-complete {{
            background-color: #d4edda;
            color: #155724;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .status-partial {{
            background-color: #fff3cd;
            color: #856404;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .status-missing {{
            background-color: #f8d7da;
            color: #721c24;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .rate {{
            font-weight: bold;
            color: #667eea;
        }}
        .text-list {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .text-detail {{
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            margin: 2px 0;
            font-size: 0.9em;
        }}
        .found-text {{
            color: #28a745;
        }}
        .missing-text {{
            color: #dc3545;
        }}
        .spec-id {{
            background: #667eea;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 피그마 디자인 텍스트 검수 보고서</h1>
            <p>생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(matches) + len(issues)}</div>
                <div class="stat-label">전체 설계서 항목</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([m for m in matches if m['status'] == 'complete'])}</div>
                <div class="stat-label">완전 구현</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([m for m in matches if m['status'] == 'partial'])}</div>
                <div class="stat-label">부분 구현</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(issues)}</div>
                <div class="stat-label">미구현</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>✅ 구현된 텍스트들</h2>
                <table>
                    <thead>
                        <tr>
                            <th>설계서 ID</th>
                            <th>설계서 항목</th>
                            <th>필요한 텍스트</th>
                            <th>구현된 텍스트</th>
                            <th>구현률</th>
                            <th>상태</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 구현된 항목들
        for match in matches:
            html_content += f"""
                        <tr>
                            <td><span class="spec-id">{match['spec_id']}</span></td>
                            <td><strong>{match['spec_name']}</strong></td>
                            <td class="text-list">
            """
            
            for text in match['required_texts']:
                html_content += f'<div class="text-detail">{text}</div>'
            
            html_content += """
                            </td>
                            <td class="text-list">
            """
            
            for found in match['found_texts']:
                html_content += f'<div class="text-detail found-text">✓ {found["found"]}</div>'
            
            for missing in match['missing_texts']:
                html_content += f'<div class="text-detail missing-text">✗ {missing}</div>'
            
            html_content += f"""
                            </td>
                            <td class="rate">{match['implementation_rate']:.1%}</td>
                            <td><span class="status-{match['status']}">{'완전 구현' if match['status'] == 'complete' else '부분 구현'}</span></td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>⚠️ 미구현된 텍스트들</h2>
                <table>
                    <thead>
                        <tr>
                            <th>설계서 ID</th>
                            <th>설계서 항목</th>
                            <th>필요한 텍스트</th>
                            <th>문제점</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 미구현된 항목들
        for issue in issues:
            html_content += f"""
                        <tr>
                            <td><span class="spec-id">{issue['spec_id']}</span></td>
                            <td><strong>{issue['spec_name']}</strong></td>
                            <td class="text-list">
            """
            
            for text in issue['required_texts']:
                html_content += f'<div class="text-detail missing-text">✗ {text}</div>'
            
            html_content += f"""
                            </td>
                            <td><span class="status-missing">모든 필요한 텍스트가 구현되지 않았습니다.</span></td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def run_check(self, design_file: str, spec_file: str = None) -> str:
        """전체 검수 프로세스 실행"""
        print("🔍 피그마 디자인 텍스트 검수를 시작합니다...")
        
        # 1. 디자인 요소 추출
        print("📋 디자인 텍스트 요소를 추출하는 중...")
        self.design_elements = self.extract_design_elements(design_file)
        print(f"   - {len(self.design_elements)}개의 텍스트 요소를 찾았습니다.")
        
        # 2. 설계서 요소 로드
        print("📖 설계서 요소를 로드하는 중...")
        if spec_file:
            self.spec_elements = self.load_specification_from_file(spec_file)
        else:
            print("❌ 설계서 파일이 필요합니다.")
            return None
        print(f"   - {len(self.spec_elements)}개의 설계서 요소를 로드했습니다.")
        
        # 3. 요소 비교
        print("🔍 텍스트 구현 여부를 확인하는 중...")
        matches, issues = self.compare_elements()
        print(f"   - {len(matches)}개 구현됨, {len(issues)}개 미구현")
        
        # 4. HTML 보고서 생성
        print("📊 HTML 보고서를 생성하는 중...")
        html_content = self.generate_html_report(matches, issues)
        
        # 5. 파일 저장
        report_file = "design_text_check_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 검수 완료! 보고서가 {report_file}에 저장되었습니다.")
        
        return report_file

def main():
    checker = DesignChecker()
    
    # 검수 실행 (실제 설계서 파일 사용)
    report_file = checker.run_check('figma_detailed.json', 'specification.json')
    
    # 브라우저에서 보고서 열기
    if report_file:
        try:
            webbrowser.open(f'file://{os.path.abspath(report_file)}')
            print("🌐 브라우저에서 보고서를 열었습니다.")
        except:
            print(f"📄 보고서 파일 위치: {os.path.abspath(report_file)}")

if __name__ == "__main__":
    main()

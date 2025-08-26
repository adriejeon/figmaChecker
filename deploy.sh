#!/bin/bash

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

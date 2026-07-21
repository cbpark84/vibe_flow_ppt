#!/usr/bin/env bash
# vibe_flow_ppt — macOS 종료 스크립트
echo "🛑 vibe_flow_ppt 종료 중..."
pkill -f "arq engine.worker" 2>/dev/null && echo "  ✓ ARQ 워커 종료" || true
pkill -f "uvicorn api.main"  2>/dev/null && echo "  ✓ FastAPI 종료"  || true
pkill -f "next-server"       2>/dev/null && echo "  ✓ Next.js 종료"  || true
pkill -f "next dev"          2>/dev/null || true
brew services stop redis     2>/dev/null && echo "  ✓ Redis 종료"    || true
echo "✅ 종료 완료"

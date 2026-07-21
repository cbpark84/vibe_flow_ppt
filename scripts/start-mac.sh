#!/usr/bin/env bash
# ============================================================
#  vibe_flow_ppt — macOS 원클릭 실행 스크립트
#  사용법: bash scripts/start-mac.sh
# ============================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}🚀 vibe_flow_ppt 시작${NC}"
echo "=================================================="

# ── 사전 확인 ──────────────────────────────────────────────
check_cmd() { command -v "$1" &>/dev/null || { echo -e "${RED}❌ '$1' 없음. README 설치 가이드 참조.${NC}"; exit 1; }; }
check_cmd python3
check_cmd brew
check_cmd node

# 가상환경 확인
if [ ! -f "venv/bin/activate" ]; then
  echo -e "${YELLOW}⚠  가상환경 없음. 생성 중...${NC}"
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt -q
else
  source venv/bin/activate
fi

# .env 확인
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}⚠  .env 없음 → .env.example 복사${NC}"
  cp .env.example .env
  echo -e "${RED}❗ .env 파일에 API 키를 설정한 뒤 다시 실행하세요.${NC}"
  exit 1
fi

# ── 1. Redis ─────────────────────────────────────────────
echo -e "${YELLOW}[1/4] Redis 시작...${NC}"
if brew services list | grep -q "redis.*started"; then
  echo -e "  ${GREEN}✓ Redis 이미 실행 중${NC}"
else
  brew services start redis
  echo -e "  ${GREEN}✓ Redis 시작됨${NC}"
fi

# ── 2. ARQ 워커 (백그라운드) ────────────────────────────
echo -e "${YELLOW}[2/4] ARQ 워커 시작...${NC}"
mkdir -p logs
arq engine.worker.settings.WorkerSettings > logs/arq-worker.log 2>&1 &
ARQ_PID=$!
echo -e "  ${GREEN}✓ ARQ 워커 PID: ${ARQ_PID}  (로그: logs/arq-worker.log)${NC}"

# ── 3. FastAPI (백그라운드) ──────────────────────────────
echo -e "${YELLOW}[3/4] FastAPI 서버 시작...${NC}"
uvicorn api.main:app --host 0.0.0.0 --port 8000 > logs/fastapi.log 2>&1 &
API_PID=$!
echo -e "  ${GREEN}✓ FastAPI PID: ${API_PID}  (로그: logs/fastapi.log)${NC}"

# FastAPI 준비 대기 (최대 15초)
echo -n "  서버 준비 대기"
for i in $(seq 1 15); do
  sleep 1; echo -n "."
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e " ${GREEN}준비됨${NC}"; break
  fi
done

# ── 4. Next.js (전경) ────────────────────────────────────
echo -e "${YELLOW}[4/4] Next.js 웹앱 시작...${NC}"
echo ""
echo -e "${GREEN}=================================================="
echo -e "  ✅ 실행 완료!"
echo -e "  🌐 웹앱:     http://localhost:3000"
echo -e "  🔧 API:      http://localhost:8000"
echo -e "  📖 Swagger:  http://localhost:8000/docs"
echo -e "=================================================="
echo -e "  종료: Ctrl+C${NC}"
echo ""

cleanup() {
  echo -e "\n${YELLOW}🛑 종료 중...${NC}"
  kill $ARQ_PID $API_PID 2>/dev/null || true
  brew services stop redis 2>/dev/null || true
  echo -e "${GREEN}✅ 종료 완료${NC}"
}
trap cleanup EXIT

cd web && pnpm dev

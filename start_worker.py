"""
ARQ Worker 시작 스크립트 (Windows/Mac 호환)

arq CLI의 dotted-path import 문제를 우회하여 직접 실행.
sys.path.insert(0, project_root)로 프로젝트 루트를 명시적으로 추가.

실행:
  python start_worker.py
"""
import sys
import os

# 프로젝트 루트를 sys.path 맨 앞에 명시적으로 추가
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"[ARQ] project_root: {project_root}")
print(f"[ARQ] sys.path[0]: {sys.path[0]}")

from arq import run_worker
from engine.worker.settings import WorkerSettings

if __name__ == '__main__':
    run_worker(WorkerSettings)

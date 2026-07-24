"""
ARQ Worker 시작 스크립트 (Windows/Mac 호환)

arq CLI의 dotted-path import 문제를 우회하여 직접 실행.
sys.path.insert(0, project_root)로 프로젝트 루트를 명시적으로 추가.
__init__.py 파일이 누락된 경우 자동으로 생성.

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

# engine/__init__.py 파일 확인 및 생성
engine_init_path = os.path.join(project_root, "engine", "__init__.py")
if not os.path.exists(engine_init_path):
    os.makedirs(os.path.dirname(engine_init_path), exist_ok=True)
    with open(engine_init_path, "w") as f:
        f.write("")
    print(f"[ARQ] Created: {engine_init_path}")
else:
    print(f"[ARQ] Found: {engine_init_path}")

# engine/worker/__init__.py 파일 확인 및 생성
worker_init_path = os.path.join(project_root, "engine", "worker", "__init__.py")
if not os.path.exists(worker_init_path):
    os.makedirs(os.path.dirname(worker_init_path), exist_ok=True)
    with open(worker_init_path, "w") as f:
        f.write("")
    print(f"[ARQ] Created: {worker_init_path}")
else:
    print(f"[ARQ] Found: {worker_init_path}")

from arq import run_worker
from engine.worker.settings import WorkerSettings

if __name__ == '__main__':
    run_worker(WorkerSettings)

"""
ARQ Worker 시작 스크립트 (Windows/Mac 호환)

arq CLI의 dotted-path import 문제를 우회하여 직접 실행.
sys.path.insert(0, project_root)로 프로젝트 루트를 명시적으로 추가.
engine/ 하위 모든 패키지에 __init__.py 파일이 존재하도록 재귀적으로 보장.

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

# engine/ 하위 모든 패키지 디렉토리에 __init__.py 재귀적으로 보장
engine_dir = os.path.join(project_root, "engine")
print(f"\n[ARQ] 디렉토리 구조 및 __init__.py 확인 시작...")
for dirpath, dirnames, filenames in os.walk(engine_dir):
    # 현재 디렉토리 레벨 표시
    rel_path = os.path.relpath(dirpath, project_root)
    print(f"[ARQ] 검사: {rel_path}")

    init_file = os.path.join(dirpath, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("")
        print(f"[ARQ]   ✓ 생성함: {os.path.relpath(init_file, project_root)}")
    else:
        print(f"[ARQ]   ✓ 존재함: {os.path.relpath(init_file, project_root)}")

print(f"\n[ARQ] engine/ 패키지 구조 준비 완료. Import 시작...\n")

from arq import run_worker
from engine.worker.settings import WorkerSettings

if __name__ == '__main__':
    run_worker(WorkerSettings)

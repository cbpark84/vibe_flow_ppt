# 스케일 업 가이드

## 현재 구성 (중규모 / 10~50 동시 사용자)

```
[Next.js] → [FastAPI] → [ARQ Job Queue] → [Redis]
                                      ↓
                              [ARQ Worker × 1~3]
```

- **FastAPI**: POST /generate로 즉시 job_id 반환 (< 100ms)
- **ARQ Worker**: 백그라운드 PPT 생성 처리
- **Redis**: 잡 상태 및 결과 저장 (1시간 TTL)

### 현재 설정

| 설정 | 값 | 의미 |
|------|-----|------|
| `max_jobs` | 10 | 워커 1개당 최대 동시 작업 |
| `job_timeout` | 300초 | 작업 최대 실행 시간 |
| `keep_result` | 3600초 | 결과 Redis 보관 시간 |

### 워커 추가로 처리량 향상

```bash
# 터미널 1
arq engine.worker.settings.WorkerSettings

# 터미널 2
arq engine.worker.settings.WorkerSettings

# 터미널 3 (선택)
arq engine.worker.settings.WorkerSettings
```

워커 3개 × max_jobs 10 = **최대 30개 동시 처리**

---

## 대규모로 업그레이드해야 할 시점

아래 중 하나라도 해당되면 Celery 전환을 고려하세요:

| 신호 | 기준 |
|------|------|
| 동시 사용자 | 50명 초과 |
| 작업 큐 대기 | 상시 10건 이상 |
| 워커 머신 | 여러 서버로 분산 필요 |
| 작업 우선순위 | 유료 사용자 우선 처리 등 |
| 모니터링 | Flower, Grafana 등 고급 모니터링 필요 |

### 대규모 구성 (Celery + RabbitMQ/Redis)

```
[Next.js] → [FastAPI] → [RabbitMQ / Redis]
                                ↓
                     [Celery Workers × N (멀티 머신)]
                                ↓
                          [Flower 모니터링]
```

### 마이그레이션 체크리스트

- [ ] `celery` 설치 및 `requirements.txt` 업데이트
- [ ] `engine/worker/tasks.py` → `@celery_app.task` 데코레이터 변환
- [ ] `engine/worker/settings.py` → `celery_app = Celery(...)` 설정
- [ ] Redis 또는 RabbitMQ 브로커 설정
- [ ] Flower 모니터링 설치: `pip install flower`
- [ ] 워커 머신별 `celery -A engine.worker worker --concurrency=8` 실행

### 마이그레이션 소요 예상 시간

ARQ → Celery 전환은 태스크 함수 시그니처 변경이 주 작업.
**예상 2~4시간** (테스트 포함)

---

## Redis 튜닝 (중규모)

```bash
# redis.conf 권장 설정
maxmemory 512mb
maxmemory-policy allkeys-lru
save ""                    # 잡 큐 전용이면 영속성 불필요
```

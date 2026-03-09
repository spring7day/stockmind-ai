.PHONY: dev dev-logs build stop clean logs backend-shell frontend-shell test help

# ============================================================
# StockMind AI — 개발 명령어 모음
# ============================================================

## dev: 모든 서비스를 백그라운드에서 실행
dev:
	docker-compose up -d
	@echo ""
	@echo "StockMind AI 실행 중"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "로그 확인: make logs"

## dev-logs: 모든 서비스를 포그라운드에서 실행 (로그 출력)
dev-logs:
	docker-compose up

## build: 모든 Docker 이미지 빌드 (캐시 없이)
build:
	docker-compose build --no-cache

## stop: 모든 서비스 중지
stop:
	docker-compose down

## clean: 모든 서비스 및 볼륨 제거 (데이터 삭제 주의)
clean:
	docker-compose down -v
	@echo "볼륨 및 컨테이너 모두 제거되었습니다."

## logs: 모든 서비스 로그 실시간 출력
logs:
	docker-compose logs -f

## backend-shell: 백엔드 컨테이너 bash 셸 접속
backend-shell:
	docker-compose exec backend bash

## frontend-shell: 프론트엔드 컨테이너 sh 셸 접속
frontend-shell:
	docker-compose exec frontend sh

## test: 테스트 실행 (백엔드 pytest)
test:
	docker-compose exec backend python -m pytest tests/ -v

## test-local: 로컬 환경에서 백엔드 테스트 실행
test-local:
	cd src/backend && python -m pytest tests/ -v

## migrate: 데이터베이스 마이그레이션 실행
migrate:
	docker-compose exec backend python -m alembic upgrade head

## ps: 실행 중인 컨테이너 상태 확인
ps:
	docker-compose ps

## env: .env.example을 .env로 복사 (최초 설정)
env:
	@if [ -f .env ]; then \
		echo ".env 파일이 이미 존재합니다. 덮어쓰려면 수동으로 삭제 후 재실행하세요."; \
	else \
		cp .env.example .env; \
		echo ".env 파일이 생성되었습니다. API 키를 입력하세요: .env"; \
	fi

## help: 사용 가능한 명령어 목록 표시
help:
	@echo ""
	@echo "StockMind AI — 개발 명령어"
	@echo "========================================"
	@grep -E '^## ' Makefile | sed 's/## /  make /' | column -t -s ':'
	@echo ""

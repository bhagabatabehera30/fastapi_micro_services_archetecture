up:
	docker compose -f docker-compose.yml up -d

build:
	docker compose -f docker-compose.yml up --build -d

buildCache:
	docker compose -f docker-compose.yml build --no-cache

down:
	docker compose -f docker-compose.yml down

restart:
	docker compose -f docker-compose.yml down && docker compose -f docker-compose.yml up -d

dstart:
	docker compose up --build
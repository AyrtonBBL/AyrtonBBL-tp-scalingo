web: cd api && uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'
postdeploy: cd api && alembic upgrade head

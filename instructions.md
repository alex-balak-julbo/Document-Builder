# Document Builder (Flask + MySQL + Vue 3 + Tailwind)

## Backend
    mysql -u root -p -e "CREATE DATABASE docbuilder CHARACTER SET utf8mb4;"
    cd backend && python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt && cp .env.example .env   # edit SECRET_KEY and DB_* settings
    flask --app app init-db
    flask --app app create-user you@company.com
    flask --app app run

## Frontend
    cd frontend && npm install && npm run dev      # http://localhost:5173 (proxies /api to Flask)

## Production
`npm run build`, serve `frontend/dist` with nginx on the same origin as the API (`/api` -> gunicorn), over HTTPS.
Set `SESSION_COOKIE_SECURE=true` in the environment when using HTTPS.

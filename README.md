# RHACbot Control Panel (Monorepo)

This repository contains a React frontend (`rhacbot/`) and a Flask backend (`backend/`) used to manage GroupMe chats for buildings.

Quick start (development)

1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Copy .env.example to .env and fill values
python app.py
```

2. Frontend

```powershell
cd rhacbot
npm install
npm start
```

Environment variables

- See `backend/.env.example` for the server-side variables. Important ones:
  - GROUPME_ACCESS_TOKEN
  - MONGODB_URI (optional for dev)
  - SECRET_KEY
  - EXECUTIVE_PASSWORD

Security and deployment notes

- Do not store secrets in client-side environment variables (those prefixed with `REACT_APP_`).
- Use a production WSGI server (Gunicorn, uWSGI, Waitress) behind a reverse proxy (nginx) and run under a process manager.
- Rotate secrets if they were committed accidentally.

What's included

- `backend/` — Flask app and README
- `rhacbot/` — React frontend and README

Next steps I can help with

- Add health endpoint and tests
- Dockerize frontend and backend
- Add CI to run lint/tests and build

Tell me which next step you'd like me to implement and I'll proceed.

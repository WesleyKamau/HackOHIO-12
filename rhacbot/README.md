# RHACbot Frontend

This is the React frontend for the RHACbot Control Panel (folder: `rhacbot`). It provides the UI for adding floor chats and sending messages to GroupMe groups.

Quick start (development)

```powershell
cd rhacbot
npm install
npm start
```

Build for production

```powershell
npm run build
```

Environment variables

- `REACT_APP_API_URL` (optional): Base URL for the backend API (e.g. `http://localhost:5000`). When omitted the app will call relative `/api` endpoints.

Security

- Never expose secrets via `REACT_APP_` variables. Keep tokens and passwords on the server.

Notes

- The frontend calls `/api/auth` to authenticate executive users and `/api/messages/send` to send messages. Server validates the admin password.
- If you want a Dockerfile or a small static server script for the built app, I can add one.

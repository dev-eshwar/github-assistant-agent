# Backend Storage Component

- **Source Files:**
  - [server/server.js](file:///C:/Users/eshcs/OneDrive/Desktop/Antigravity%20projects/githubrepo_assistant/math-galaxy/server/server.js)

## Responsibility

The Backend Storage Component provides the backend runtime environment for the application:
- It initializes an Express.js HTTP server.
- It exposes GET and POST API endpoints at `/api/progress` to load and persist student stars, current levels, strengths, and answer logs.
- It reads/writes state data to a flat, local file located at `server/progress.json`.
- It serves the production React client assets built in the `dist/` directory.
- It acts as single-page application fallback routing in production mode.

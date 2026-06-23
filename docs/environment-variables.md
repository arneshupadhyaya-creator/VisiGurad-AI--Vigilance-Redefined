# Environment Variables Reference

VisiGuard AI configuration is managed through dotenv files in the backend and Vite configurations in the frontend.

---

## Backend Configurations
Create a `.env` file inside `apps/backend/`.

| Variable | Description | Default Value | Production Recommendation |
|---|---|---|---|
| `PORT` | Local web server port | `5000` | Match port configured in reverse-proxy |
| `NODE_ENV` | Running environment | `development` | Set to `production` |
| `MONGO_URI` | MongoDB connection URI | `mongodb://127.0.0.1:27017/visiguard` | Set to private MongoDB cluster string |
| `JWT_SECRET` | Secret key to sign session tokens | `DUMMY_REPLACE_WITH_REAL_SECRET` | Generate a cryptographically random string |
| `JWT_EXPIRES_IN` | Token validity timeframe | `24h` | Reduce to `15m` with refresh token integrations |
| `AI_MODEL_ENDPOINT`| Target URI for the future FastAPI model | `http://localhost:8000/predict` | Internal private cloud endpoint IP |
| `REDIS_HOST` | Redis host for task queues | `127.0.0.1` | Host address of Redis cluster |
| `REDIS_PORT` | Redis server port | `6379` | `6379` |

---

## Frontend Configurations
Create a `.env` file inside `apps/frontend/`.

| Variable | Description | Default Value |
|---|---|---|
| `VITE_API_BASE_URL`| Base endpoint of the Express backend | `http://localhost:5000/api` |

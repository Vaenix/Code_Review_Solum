# SecC Run Instructions

## Overview

`SecC` contains:

- `backend/`: FastAPI API
- `frontend/`: React + Vite dashboard

The app runs locally with:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:4173`

## 1. Start the Backend

Open a terminal:

```bash
cd ../Code_Review_Solum/SecC/backend
./venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

After startup, verify:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected result: a JSON response with `status: "ok"`.

## 2. Start the Frontend

Open a second terminal:

```bash
cd ../Code_Review_Solum/SecC/frontend
npm run dev
```

Then open:

```text
http://127.0.0.1:4173/
```

## 3. Build the Frontend

If you only want to verify production build:

```bash
cd ../Code_Review_Solum/SecC/frontend
npm run build
```

## 4. Optional API Base URL

The frontend defaults to:

```text
http://127.0.0.1:8000/api
```

If needed, you can override it with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api npm run dev
```

## 5. Common Issues

If the backend works but the frontend page stays blank:

- Make sure you opened `http://127.0.0.1:4173/`, not the raw `index.html` file.
- Hard refresh the browser: `Ctrl+Shift+R`.
- Check that the backend is still running on port `8000`.

If port `8000` is already in use:

- Stop the old backend process, then restart the command above.

If port `4173` is already in use:

- Stop the old Vite process, then rerun `npm run dev`.

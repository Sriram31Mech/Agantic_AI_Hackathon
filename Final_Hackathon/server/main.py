from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from agents.okr_parser import parse_okr, load_context

app = FastAPI()

# Path to the React build directory
FRONTEND_BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../client/build'))

# Mount the static files (React build)
if os.path.exists(FRONTEND_BUILD_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_BUILD_DIR, html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origin in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "OK", "message": "Fina_Hackathon backend is running."}

@app.post("/api/parse-okr")
async def parse_okr_endpoint(request: Request):
    data = await request.json()
    okr_text = data.get("okr_text", "")
    return parse_okr(okr_text)

# Catch-all route for React client-side routing
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build not found. Please run 'npm run build' in the client directory."}

if __name__ == "__main__":
    print("[INFO] Loading RAG context...")
    load_context()
    print("[INFO] Starting FastAPI server on port 5050...")
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=True)

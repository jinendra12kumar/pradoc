"""
PraDoc Health — FastAPI Application Entrypoint
Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from app import app  # noqa: F401 — exposes the FastAPI instance

@app.get("/")
def read_root():
    return {"message": "Welcome to PraDoc Health API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

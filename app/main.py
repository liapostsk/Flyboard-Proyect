from fastapi import FastAPI

app = FastAPI(title="Flyboard Agent Router API")

@app.get("/health")
def health():
    return {"status": "ok"}

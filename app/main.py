from fastapi import FastAPI
from app.api.routes import router

# Crear instancia de FastAPI
app = FastAPI(title="Flyboard Agent Router API")
app.include_router(router)

@app.get("/health")
def health():
	return {"status": "ok"}

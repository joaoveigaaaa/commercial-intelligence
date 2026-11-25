from fastapi import FastAPI

app = FastAPI(title="Inteligência Comercial")


@app.get("/saude")
def saude() -> dict:
    return {"status": "ok"}

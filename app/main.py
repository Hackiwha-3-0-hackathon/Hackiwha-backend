from fastapi import FastAPI

app = FastAPI(
    title="Hackiwha API"
)

@app.get("/")
def root():
    return {"message": "Hello world!"}
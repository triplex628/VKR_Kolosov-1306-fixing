import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from server.routers import users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fitness API")

# вычисляем абсолютный путь к папке server/static
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # or restrict to ["http://localhost:5500","http://127.0.0.1:5500"] if you serve statics on that port
    allow_credentials=True,
    allow_methods=["*"],         # this will allow OPTIONS (and GET, POST, etc)
    allow_headers=["*"],         # allow Content-Type, Authorization, etc
)

# подключаем остальные роутеры
from server.routers import users, workouts, ml, stream, auth, poses, packages, sessions, stats

app.include_router(users.router)
app.include_router(workouts.router)
app.include_router(ml.router)
app.include_router(stream.router, tags=["Stream"])
app.include_router(auth.router)
app.include_router(poses.router)
app.include_router(packages.router)
app.include_router(sessions.router)
app.include_router(stats.router)

# теперь монтируем корректную директорию
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="frontend")

@app.get("/")
async def root():
    return {"message": "Fitness API is running!"}

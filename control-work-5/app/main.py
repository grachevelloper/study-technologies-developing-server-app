from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Query, WebSocket, WebSocketDisconnect

from app.dependencies import get_current_user, get_storage
from app.routers import admin, tasks, users
from app.schemas import HealthResponse, RoomUsersResponse, UserContext
from app.storage import AppStorage

app = FastAPI(title="Control Work 5", version="1.0.0")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "env": os.getenv("APP_ENV", "local")}


@app.get("/rooms/{room_id}/users", response_model=RoomUsersResponse, tags=["rooms"])
def get_room_users(
    room_id: str,
    storage: AppStorage = Depends(get_storage),
) -> dict[str, object]:
    return {"room_id": room_id, "users": storage.room_manager.get_users(room_id)}


@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: str,
    username: str = Query(...),
    storage: AppStorage = Depends(get_storage),
) -> None:
    normalized_username = username.strip()
    if not normalized_username:
        await websocket.close(code=1008)
        return

    room_manager = storage.room_manager
    await room_manager.connect(room_id, normalized_username, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            if payload.get("type") != "message":
                continue
            text = str(payload.get("text", ""))
            if len(text) > 300:
                await websocket.send_json({"type": "error", "detail": "Message is too long"})
                continue
            await room_manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": normalized_username,
                    "text": text,
                },
            )
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, normalized_username, websocket)

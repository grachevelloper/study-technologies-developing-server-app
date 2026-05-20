from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.rooms[room_id].append({"username": username, "websocket": websocket})
        await self.broadcast(
            room_id,
            {"type": "joined", "room_id": room_id, "username": username},
        )

    def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        connections = self.rooms.get(room_id, [])
        self.rooms[room_id] = [
            connection
            for connection in connections
            if not (
                connection["username"] == username and connection["websocket"] is websocket
            )
        ]
        if not self.rooms[room_id]:
            self.rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, payload: dict[str, Any]) -> None:
        for connection in self.rooms.get(room_id, []):
            await connection["websocket"].send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        return [connection["username"] for connection in self.rooms.get(room_id, [])]


class AppStorage:
    def __init__(self) -> None:
        self.tasks: dict[int, dict[str, Any]] = {}
        self.next_task_id = 1
        self.room_manager = RoomManager()

    def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        task = {"id": self.next_task_id, **data}
        self.tasks[self.next_task_id] = task
        self.next_task_id += 1
        return task

    def reset(self) -> None:
        self.tasks.clear()
        self.next_task_id = 1
        self.room_manager = RoomManager()


storage = AppStorage()


def reset_state() -> None:
    storage.reset()

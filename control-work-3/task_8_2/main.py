from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from database import create_tables, get_db_connection

create_tables()

app = FastAPI(title="Task 8.2 — Todo CRUD")



class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TodoUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool


class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool


def get_todo_or_404(todo_id: int) -> dict:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id={todo_id} not found",
        )
    return dict(row)


@app.post("/todos", status_code=status.HTTP_201_CREATED, response_model=Todo)
def create_todo(todo: TodoCreate):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, 0),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    result = dict(row)
    result["completed"] = bool(result["completed"])
    return result


@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int):
    row = get_todo_or_404(todo_id)
    row["completed"] = bool(row["completed"])
    return row


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoUpdate):
    get_todo_or_404(todo_id) 
    conn = get_db_connection()
    conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, int(todo.completed), todo_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    result = dict(row)
    result["completed"] = bool(result["completed"])
    return result


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    get_todo_or_404(todo_id) 
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": f"Todo {todo_id} deleted successfully"}

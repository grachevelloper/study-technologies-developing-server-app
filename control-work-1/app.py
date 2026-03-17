from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from models import User, UserWithAge, Feedback, FeedbackResponse, CalculateResponse, UserResponse
from typing import List

app = FastAPI(
    title="Контрольная работа №1",
    description="Технологии разработки серверных приложений",
    version="1.0.0"
)

feedbacks_db = []


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}


@app.get("/html")
async def get_html():
    return FileResponse("index.html")


@app.post("/calculate", response_model=CalculateResponse)
async def calculate(num1: int, num2: int):
    result = num1 + num2
    return {"result": result}


user_instance = User(name="Николай Грачев", id=1)

@app.get("/users")
async def get_user():
    return user_instance


@app.post("/user", response_model=UserResponse)
async def check_adult(user: UserWithAge):
    is_adult = user.age >= 18
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": is_adult
    }


@app.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(feedback: Feedback):
    feedbacks_db.append(feedback.dict())
    return {"message": f"Feedback received. Thank you, {feedback.name}."}


feedback_list = []

@app.post("/feedback/validated", response_model=FeedbackResponse)
async def create_validated_feedback(feedback: Feedback):
    feedback_list.append(feedback.dict())
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}


@app.get("/feedbacks/all")
async def get_all_feedbacks():
    return {
        "feedbacks_db": feedbacks_db,
        "feedback_list": feedback_list
    }


@app.get("/feedbacks/count")
async def get_feedbacks_count():
    return {
        "total_feedbacks": len(feedbacks_db) + len(feedback_list),
        "feedback_v1_count": len(feedbacks_db),
        "feedback_v2_count": len(feedback_list)
    }


@app.get("/autoreload-test")
async def autoreload_test():
    return {"message": "Автоперелоад действительно работает"}


alt_app = FastAPI()

@alt_app.get("/alt")
async def alt_root():
    return {"message": "Это альтернативное приложение с другим именем переменной"}
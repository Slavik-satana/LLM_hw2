from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from model.inference import PhoebeBot

app = FastAPI()
templates = Jinja2Templates(directory="templates")
bot = PhoebeBot()

class UserQuery(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat/")
async def chat(request: UserQuery):
    response = bot.get_response(request.query)
    return {"response": response}
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.graph import app_graph

app = FastAPI(title="Verify Live")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    text: str


@app.post("/verify")
def verify(request: VerifyRequest):
    result = app_graph.invoke({
        "input_text": request.text,
        "claims": [],
        "evidence": [],
        "verdicts": [],
        "search_iterations": 0,
    })
    return {
        "claims": [c.model_dump() for c in result["claims"]],
        "verdicts": [v.model_dump() for v in result["verdicts"]],
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
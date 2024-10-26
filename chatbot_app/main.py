import logging
import logging.config

from fastapi import FastAPI
from graph.graph import graph_flow
from schemas.chat_schemas import QuestionRequest

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

logger = logging.getLogger(__name__)

app = FastAPI()

config = {
    "configurable": {
        "thread_id": "si_thu_phyo_thread_1",
    }
}


# Define the request model


@app.post("/chat")
def chat(request: QuestionRequest):
    # Use the question from the request body
    response = graph_flow.invoke(input={"question": request.question}, config=config)
    return {"response": response}


@app.post("/clear_memory")
def clear():
    graph_flow.update_state(
        config,
        {
            "question": "",
            "generation": "TTTT",
            "web_search": False,
            "documents": [],
            "chat_history": [],
        },
    )
    return {"success": True}

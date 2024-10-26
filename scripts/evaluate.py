import os

import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv
from langchain.callbacks.tracers import LangChainTracer
from langsmith import Client
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness

load_dotenv()

tracer = LangChainTracer(project_name="chatbot-evaluation-experiments")

dataset_name = os.getenv("LANGSMITH_DATASET_NAME")

metrics = [
    answer_relevancy,
    faithfulness,
]

langsmith_client = Client()

examples = langsmith_client.list_examples(dataset_name=dataset_name)
example_data = [
    {
        "question": example.outputs["question"],
        "answer": example.outputs["generation"],
        "contexts": [
            document["page_content"] for document in example.outputs["documents"]
        ],
    }
    for example in examples
]

dataset = Dataset.from_pandas(pd.DataFrame(data=example_data))

evaluate(dataset, metrics=metrics, callbacks=[tracer])

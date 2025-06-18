# src/evaluator.py
import httpx
import httpx._models as models

def _normalize_header_value(value, encoding):
    if isinstance(value, str):
        return value.encode("utf-8")
    return value
models._normalize_header_value = _normalize_header_value
models.Headers._encoding = "utf-8"

from dotenv import load_dotenv
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

load_dotenv()

# Chuẩn bị prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Bạn là chuyên gia đánh giá phỏng vấn. Hãy đọc câu hỏi và câu trả lời sau và cho điểm:"        
    ),
    HumanMessagePromptTemplate.from_template(
        "Câu hỏi: {question}\nCâu trả lời: {answer}\n\n"        
        "Trả về một JSON với các trường fluency, knowledge, soft_skills."        
    )
])
llm = ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo")
eval_chain = prompt | llm

def evaluate_single(question: str, answer: str) -> dict:
    """Đánh giá một câu hỏi và câu trả lời, trả về dict điểm."""
    ai_response = eval_chain.invoke({"question": question, "answer": answer})
    # Ai_response có thể là AIMessage
    text = getattr(ai_response, 'content', ai_response)
    try:
        return json.loads(text)
    except Exception:
        return {"fluency": 0, "knowledge": 0, "soft_skills": 0}

def evaluate_responses(all_qa: list) -> dict:
    """Nhận list các dict {question, answer}. Trả về điểm trung bình và chi tiết."""
    totals = {"fluency": 0, "knowledge": 0, "soft_skills": 0}
    detailed = []
    for qa in all_qa:
        scores = evaluate_single(qa['question'], qa['answer'])
        detailed.append({**qa, **scores})
        for k in totals:
            totals[k] += scores.get(k, 0)
    n = len(all_qa)
    averaged = {k: round((totals[k] / n), 2) if n else 0 for k in totals}
    return {"averaged": averaged, "detailed": detailed}

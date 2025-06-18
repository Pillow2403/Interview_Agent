# src/ui.py
import httpx
import httpx._models as models

# Monkey-patch HTTPX để chấp nhận UTF-8 cho header values

def _normalize_header_value(value, encoding):
    if isinstance(value, str):
        return value.encode("utf-8")
    return value
models._normalize_header_value = _normalize_header_value
models.Headers._encoding = "utf-8"

import os
import json
import gradio as gr
from interviewer import InterviewerAgent
from evaluator import evaluate_responses
from report_generator import generate_pdf_report
from mailer import send_email_report

# Hàm load danh sách câu hỏi từ file JSON
def load_questions(domain: str) -> list:
    path = os.path.join(os.path.dirname(__file__), '../data/scripts', f'{domain.lower()}_questions.json')
    with open(path, encoding='utf-8') as f:
        script = json.load(f)
    questions = []
    for key in sorted(script.keys()):
        questions.extend(script[key])
    return questions

# Khởi tạo buổi phỏng vấn
def start_interview(name, role, domain):
    questions = load_questions(domain)
    chat_history = []  # List of dicts with keys 'role', 'content'
    qa_history = []
    # Assistant greeting
    welcome = f"Xin chào {name}! Bạn ứng tuyển vị trí {role} thuộc lĩnh vực {domain}."
    first_q = questions[0] if questions else "Không có câu hỏi"
    chat_history.append({"role": "assistant", "content": welcome})
    chat_history.append({"role": "assistant", "content": first_q})
    # Return: clear input, chat_history, qa_history, questions, index
    return "", chat_history, qa_history, questions, 0

# Xử lý mỗi lần ứng viên trả lời
def answer_question(user_msg, chat_history, qa_history, questions, idx, name, role, domain):
    # Append user message
    qa_history.append({"question": questions[idx], "answer": user_msg})
    chat_history.append({"role": "user", "content": user_msg})
    next_idx = idx + 1
    if next_idx < len(questions):
        # Append next question
        next_q = questions[next_idx]
        chat_history.append({"role": "assistant", "content": next_q})
        return "", chat_history, qa_history, questions, next_idx
    else:
        # End of questions: evaluate, generate PDF, send email
        scores = evaluate_responses(qa_history)
        report_path = generate_pdf_report(
            candidate_name=name,
            position=role,
            domain=domain,
            conversation_history=qa_history,
            scores=scores
        )
        send_email_report(report_path, candidate_name=name, position=role)
        chat_history.append({"role": "assistant", "content": "Phỏng vấn hoàn tất. Báo cáo đã gửi đến HR."})
        return "", chat_history, qa_history, questions, next_idx

with gr.Blocks() as demo:
    gr.Markdown("## AI Interviewer Agent – Phỏng vấn ảo tự động")
    with gr.Row():
        name_input = gr.Textbox(label="Tên ứng viên", placeholder="Nhập tên ứng viên")
        role_input = gr.Textbox(label="Chức danh", placeholder="VD: Software Engineer Intern")
        domain_input = gr.Dropdown(choices=["IT", "PM", "Data", "UI_UX Design"], label="Lĩnh vực", value="IT")

    start_btn = gr.Button("Bắt đầu phỏng vấn")
    chatbot = gr.Chatbot(label="Cuộc đối thoại", type="messages")

    qa_state = gr.State([])
    questions_state = gr.State([])
    index_state = gr.State(0)

    user_input = gr.Textbox(label="Trả lời ứng viên...", placeholder="Nhập câu trả lời và nhấn Enter")

    start_btn.click(
        fn=start_interview,
        inputs=[name_input, role_input, domain_input],
        outputs=[user_input, chatbot, qa_state, questions_state, index_state]
    )
    user_input.submit(
        fn=answer_question,
        inputs=[user_input, chatbot, qa_state, questions_state, index_state, name_input, role_input, domain_input],
        outputs=[user_input, chatbot, qa_state, questions_state, index_state]
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)


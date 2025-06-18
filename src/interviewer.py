# src/interviewer.py

import os
import json
import time
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

class InterviewerAgent:
    def __init__(self, domain: str, candidate_name: str, position: str):
        """
        domain: 'IT', 'PM' hoặc 'Data'
        candidate_name: tên ứng viên
        position: chức danh (ví dụ 'Software Engineer Intern')
        """
        load_dotenv()
        self.llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o-mini")  
        # Dùng GPT (bạn có thể thay bằng 'gpt-3.5-turbo' nếu muốn)
        
        self.domain = domain
        self.candidate_name = candidate_name
        self.position = position

        # Load kịch bản câu hỏi theo domain
        script_path = os.path.join(
            os.path.dirname(__file__),
            "../data/scripts",
            f"{domain.lower()}_questions.json"
        )
        with open(script_path, "r", encoding="utf-8") as f:
            self.question_script = json.load(f)

        # Tạo PromptTemplate cơ bản
        self.prompt_template = PromptTemplate(
            input_variables=["role", "question", "candidate_name", "position", "history"],
            template=(
                "Bạn là một người phỏng vấn với vai trò {role}. "
                "Ứng viên {candidate_name} đang ứng tuyển vị trí {position}. "
                "Lịch sử đối thoại trước đó:\n{history}\n\n"
                "Bây giờ hãy hỏi ứng viên câu hỏi sau:\n{question}\n"
                "Chỉ hỏi một câu hỏi tại một thời điểm và đợi câu trả lời."
            )
        )

    def run_interview(self):
        """
        Thực hiện lần lượt các câu hỏi từ mức độ 1 → 3.
        Lưu toàn bộ history câu hỏi + trả lời.
        """
        conversation_history = ""  # lưu dạng text nối tiếp
        all_qa = []  # danh sách dict { "question":..., "answer":... }

        # Chạy 3 level (bạn có thể tùy chỉnh số level)
        for level_key in ["level_1", "level_2", "level_3"]:
            questions = self.question_script.get(level_key, [])
            for q in questions:
                # Tạo prompt
                prompt = self.prompt_template.format(
                    role=self.domain + " Interviewer", 
                    question=q,
                    candidate_name=self.candidate_name,
                    position=self.position,
                    history=conversation_history
                )
                # Gọi LLM để hỏi (vì LLM chỉ tạo câu hỏi, còn ứng viên trả lời bằng input tay)
                # Ở đây ta giả định chatbot sẽ hỏi, nhưng để đơn giản, ta in câu hỏi ra console
                print(f"\n[Hỏi ứng viên] {q}")
                # Chờ input câu trả lời từ console (mô phỏng ứng viên trả lời)
                answer = input("Ứng viên trả lời: ").strip()
                
                # Ghi history
                conversation_history += f"Interviewer: {q}\nCandidate: {answer}\n"
                all_qa.append({"question": q, "answer": answer})

                time.sleep(0.5)  # giãn chút cho tự nhiên

        return all_qa

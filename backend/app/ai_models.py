import os
from typing import Optional, Dict, Any
import ollama
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from dotenv import load_dotenv

load_dotenv()

class AIModelHandler:
    def __init__(self):
        self.hf_model_name = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.use_ollama_backup = os.getenv("USE_OLLAMA_AS_BACKUP", "true").lower() == "true"
        self.hf_token = os.getenv("HUGGINGFACE_API_KEY")
        
        # Initialize Hugging Face model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.hf_model_name, token=self.hf_token)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.hf_model_name,
                token=self.hf_token,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.use_hf = True
        except Exception as e:
            print(f"Failed to load Hugging Face model: {str(e)}")
            self.use_hf = False
            if not self.use_ollama_backup:
                raise Exception("Failed to load primary model and backup is disabled")

    async def generate_response(self, prompt: str, max_length: int = 500) -> str:
        try:
            if self.use_hf:
                return await self._generate_hf_response(prompt, max_length)
            elif self.use_ollama_backup:
                return await self._generate_ollama_response(prompt)
            else:
                raise Exception("No available model for generation")
        except Exception as e:
            if self.use_ollama_backup and self.use_hf:
                print(f"HF model failed, falling back to Ollama: {str(e)}")
                return await self._generate_ollama_response(prompt)
            raise e

    async def _generate_hf_response(self, prompt: str, max_length: int) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    async def _generate_ollama_response(self, prompt: str) -> str:
        response = ollama.generate(
            model=self.ollama_model,
            prompt=prompt,
            stream=False
        )
        return response['response']

    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        prompt = f"""Analyze the following resume and provide insights:
        {resume_text}
        
        Please provide:
        1. Key skills
        2. Experience level
        3. Education background
        4. Potential job matches
        5. Areas for improvement
        """
        
        analysis = await self.generate_response(prompt)
        return {
            "raw_analysis": analysis,
            "model_used": "ollama" if not self.use_hf else "huggingface"
        }

    async def generate_job_description(self, role: str, requirements: list) -> str:
        prompt = f"""Generate a detailed job description for the role of {role}.
        Key requirements:
        {', '.join(requirements)}
        
        Please include:
        1. Job title
        2. Job summary
        3. Key responsibilities
        4. Required qualifications
        5. Preferred qualifications
        6. Benefits
        """
        
        return await self.generate_response(prompt)

    async def generate_interview_questions(self, job_description: str, num_questions: int = 5) -> list:
        prompt = f"""Generate {num_questions} interview questions based on this job description:
        {job_description}
        
        Include a mix of:
        1. Technical questions
        2. Behavioral questions
        3. Problem-solving scenarios
        """
        
        response = await self.generate_response(prompt)
        # Split response into individual questions
        questions = [q.strip() for q in response.split('\n') if q.strip()]
        return questions[:num_questions] 
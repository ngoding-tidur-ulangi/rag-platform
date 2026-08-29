import google.generativeai as genai
import json
from app.config.settings import settings

class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def decide_retrieval_method(self, question: str) -> dict:
        prompt = f"""
        Analyze the following question and decide if it needs 'exact' retrieval (specific surah/verse numbers) or 'semantic' retrieval (conceptual questions).
        
        If 'exact', provide the surah_number and verse_number if possible.
        
        Return a JSON object with:
        - "method": "exact" or "semantic"
        - "surah_number": int or null
        - "verse_number": int or null

        Question: {question}
        """
        response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)

    async def generate_answer(self, question: str, context_text: str) -> str:
        prompt = f"""
        Answer the following question based on the provided Quranic context.
        
        Context:
        {context_text}
        
        Question: {question}
        
        Answer:
        """
        response = self.model.generate_content(prompt)
        return response.text

from openai import OpenAI

from app.config import settings


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_embedding(self, text: str) -> list[float]:
        cleaned_text = text.replace("\n", " ").strip()

        response = self.client.embeddings.create(
            input=cleaned_text,
            model=settings.openai_embedding_model,
        )

        return response.data[0].embedding

    def generate_compliance_explanation(self, evidence: str) -> str:
        response = self.client.responses.create(
            model=settings.openai_chat_model,
            input=f"""
You are a compliance investigation assistant.
Explain why the following transaction evidence may be risky.
Keep the explanation short, specific, and evidence-based.

Evidence:
{evidence}
"""
        )

        return response.output_text

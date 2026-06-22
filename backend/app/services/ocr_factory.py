from flask import current_app

from app.services.ocr_service import GeminiOCRService, OCRService


def get_ocr_service() -> OCRService:
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    model = current_app.config.get("GEMINI_MODEL", "gemini-3.5-flash")
    return GeminiOCRService(api_key=api_key, model=model)

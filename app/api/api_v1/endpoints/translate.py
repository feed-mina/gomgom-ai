from fastapi import APIRouter, Body
from app.utils.translator import translator

router = APIRouter()

@router.post("/translate")
async def translate_texts(texts: list[str] = Body(...)):
    # 여러 문장 한 번에 번역
    results = []
    for text in texts:
        translated = await translator.translate_to_korean(text)
        results.append(translated)
    return {"translatedTexts": results}

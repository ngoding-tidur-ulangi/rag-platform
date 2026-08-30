from pydantic import BaseModel, ConfigDict

class TafsirResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    surah_number: int
    verse_number: int
    commentator: str
    text: str

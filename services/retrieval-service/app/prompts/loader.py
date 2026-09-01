from pathlib import Path

PROMPT_DIR = Path(__file__).parent

QUESTION_ROUTER_PROMPT = (
    PROMPT_DIR / "question_router.txt"
).read_text(encoding="utf-8")

ANSWER_GENERATION_PROMPT = (
    PROMPT_DIR / "answer_generation.txt"
).read_text(encoding="utf-8")
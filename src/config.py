from pathlib import Path
from dotenv import dotenv_values


CAMINHO_ENV = Path(__file__).resolve().parent.parent / ".env"
ENV = dotenv_values(CAMINHO_ENV)

GEMINI_API_KEY = ENV["GEMINI_API_KEY"]
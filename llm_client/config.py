"""Carga de API keys. No tiene efectos secundarios al importarse."""
import os
from getpass import getpass
from dotenv import load_dotenv

_KEYS = {
    "OPENAI_API_KEY": "🔑 OPENAI_API_KEY: ",
    "ANTHROPIC_API_KEY": "🔑 ANTHROPIC_API_KEY: ",
    "GOOGLE_API_KEY": "🔑 GOOGLE_API_KEY (gratis en aistudio.google.com/apikey): ",
    "GROQ_API_KEY": "🔑 GROQ_API_KEY: ",
    "HF_TOKEN": "🔑 HF_TOKEN: ",
    "DEEPSEEK_API_KEY": "🔑 DEEPSEEK_API_KEY: ",
}


def load_api_keys(interactive: bool = False) -> None:
    """Lee las keys desde el archivo .env / variables de entorno.

    Si interactive=True (útil en notebooks), pide por consola las que falten.
    """
    load_dotenv()
    if interactive:
        for nombre, prompt in _KEYS.items():
            if not os.environ.get(nombre):
                os.environ[nombre] = getpass(prompt).strip()

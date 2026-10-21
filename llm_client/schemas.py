
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, SecretStr
from enum import Enum
class Provider(str, Enum):
    """Enum de proveedores de LLM soportados."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    DEEPSEEK = "deepseek"



class LLMConfig(BaseModel):
    provider: Provider
    model: str
    api_key: Optional[SecretStr] = None
    base_url: Optional[str] = None
    temperature: float = Field(default=0.0, ge=0, le=2)

class EntidadesTecnicas(BaseModel):
    """Contrato de salida: qué extraemos de un texto técnico."""
    tecnologias: list[str] = Field(
        description="Lista de tecnologías, frameworks o lenguajes mencionados"
    )
    nivel_de_criticidad: Literal["baja", "media", "alta"] = Field(
        description="Nivel de criticidad estimado del problema técnico descrito"
    )
    resumen_tecnico: str = Field(
        description="Resumen técnico en no más de 60 palabras"
    )

    @field_validator("tecnologias")
    @classmethod
    def no_puede_estar_vacia(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("La lista de tecnologías no puede estar vacía")
        return v

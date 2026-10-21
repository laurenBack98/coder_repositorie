import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from .schemas import LLMConfig, EntidadesTecnicas
from .factory import build_llm_client


def _coerce_entidades_tecnicas(raw):
    if isinstance(raw, EntidadesTecnicas):
        return raw

    if hasattr(raw, "parsed") and raw.parsed is not None:
        return EntidadesTecnicas.model_validate(raw.parsed)

    if isinstance(raw, dict):
        return EntidadesTecnicas.model_validate(raw)

    text = raw.content if hasattr(raw, "content") else str(raw)
    if isinstance(text, list):
        text = " ".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in text
        )

    text = str(text).strip()
    if not text:
        raise ValueError("La respuesta del modelo estaba vacia")

    match = re.search(r"\{.*\}", text, re.S)
    if match:
        text = match.group(0)

    cleaned = text.replace("```json", "").replace("```", "").strip()
    try:
        payload = json.loads(cleaned)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("La respuesta del modelo no contiene JSON valido") from exc
    return EntidadesTecnicas.model_validate(payload)


def build_prompt_chain(config: LLMConfig):
    # Obtenemos el cliente LLM según la configuración
    llm_client = build_llm_client(config)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Sos un asistente técnico especializado en análisis de software. "
            "Extraé las entidades técnicas requeridas respetando estrictamente el schema. "
            "Respondé únicamente con un JSON válido con las claves tecnologias, "
            "nivel_de_criticidad y resumen_tecnico."
        ),
        ("human", "Analizá el siguiente texto técnico:\n\n{texto}")
    ])

    try:
        llm_estructurado = llm_client.with_structured_output(EntidadesTecnicas).with_retry(
            stop_after_attempt=3
        )
        return prompt | llm_estructurado
    except NotImplementedError:
        llm_compatible = llm_client.with_retry(stop_after_attempt=3)
        return prompt | llm_compatible | RunnableLambda(_coerce_entidades_tecnicas)

import os
import asyncio
import logging
from llm_client.config import load_api_keys
from llm_client.schemas import LLMConfig, Provider, EntidadesTecnicas
from llm_client.chain import build_prompt_chain
# Configuración básica de logs requerida por la consigna
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
# Función requerida por la consigna
async def process_text(chain, text: str) -> EntidadesTecnicas:
    logger.info("Iniciando procesamiento y validación del texto...")
    resultado = await chain.ainvoke({"texto": text})
    logger.info("Salida validada correctamente con Pydantic.")
    return resultado
PROVEEDORES_A_PROBAR = [
    (Provider.OPENAI, "gpt-4o-mini", "OPENAI_API_KEY"),
    (Provider.ANTHROPIC, "claude-3-5-haiku-latest", "ANTHROPIC_API_KEY"),
    (Provider.GEMINI, "gemini-1.5-flash", "GOOGLE_API_KEY"),
    (Provider.GROQ, "llama3-70b-8192", "GROQ_API_KEY"),
    (Provider.HUGGINGFACE, "mistral-7b-instruct-v0.2", "HF_TOKEN"),
    (Provider.DEEPSEEK, "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "DEEPSEEK_API_KEY")
]
TIEMPO_LIMITE_PROVEEDOR = 60

async def probar_cadena_por_proveedor(provider: Provider, model: str, env_var: str, textos: list[str]) -> None:
    api_key = os.environ.get(env_var, "").strip()
    if not api_key:
        print(f"\n[{provider.value.upper()}] Saltado: falta {env_var}.")
        return
    print(f"\n==============================")
    print(f" Probando: {provider.value.upper()} ({model})")
    print(f"==============================")
    config = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        temperature=0.0,
    )
    chain = build_prompt_chain(config)
    # 1. Prueba individual usando process_text
    print("-> Ejecucion individual (process_text / ainvoke):")
    resultado = await process_text(chain, textos[0])
    print(f" Tecnologias : {resultado.tecnologias}")
    print(f" Criticidad  : {resultado.nivel_criticidad}")
    print(f" Resumen     : {resultado.resumen_tecnico}")
    # 2. Prueba en lote con abatch
    print("\n-> Ejecucion en lote (abatch):")
    resultados_batch = await chain.abatch([{"texto": t} for t in textos[1:]])
    for idx, r in enumerate(resultados_batch, 1):
        print(f" [{idx}] Techs: {r.tecnologias} | Criticidad: {r.nivel_criticidad}")
async def main():
    load_api_keys()
    textos_prueba = [
        "El microservicio en FastAPI falló al conectar con Redis por saturación del pool.",
        "Migración del backend Django a NestJS utilizando base de datos MongoDB.",
        "Caída total de producción: el cluster de Kubernetes no responde a tráfico entrante."
    ]
    for provider, modelo, env_var in PROVEEDORES_A_PROBAR:
        try:
            await asyncio.wait_for(
                probar_cadena_por_proveedor(provider, modelo, env_var, textos_prueba),
                timeout=TIEMPO_LIMITE_PROVEEDOR,
            )
        except asyncio.TimeoutError:
            logger.error(
                "El proveedor %s superó el límite de %s segundos; se continúa con el siguiente.",
                provider.value.upper(),
                TIEMPO_LIMITE_PROVEEDOR,
            )
        except Exception:
            logger.exception(
                "Falló el proveedor %s; se continúa con el siguiente.",
                provider.value.upper(),
            )
if __name__ == "__main__":
    asyncio.run(main())
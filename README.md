# Cliente LLM multi-proveedor con LangChain

Este proyecto encapsula la creación de clientes LLM según el proveedor configurado y permite construir una cadena de prompts reutilizable para extraer entidades técnicas de texto.

Soporta los siguientes proveedores:

- OpenAI
- Anthropic
- Groq
- Gemini (Google Generative AI)
- Hugging Face
- DeepSeek (vía API compatible con OpenAI)

## ¿Qué hace el proyecto?

La aplicación centraliza tres tareas principales:

1. Validar la configuración del proveedor a través de Pydantic.
2. Instanciar el cliente correcto con `build_llm_client(...)`.
3. Construir una cadena (`prompt | llm`) que devuelva un esquema estructurado (`EntidadesTecnicas`).

## Estructura del proyecto

```text
proyecto/
├── main.py
├── .env.example
├── README.md
├── requirements.txt
├── llm_client/
│   ├── __init__.py
│   ├── chain.py
│   ├── config.py
│   ├── factory.py
│   └── schemas.py
└── .venv/   # opcional, entorno virtual local
```

## Archivos importantes

- `main.py`: script de prueba para ejecutar el flujo en varios proveedores.
- `llm_client/factory.py`: fábrica que crea el cliente LangChain según el proveedor.
- `llm_client/chain.py`: arma la cadena de prompts y aplica fallback para proveedores sin `with_structured_output`.
- `llm_client/schemas.py`: modelos Pydantic con `Provider` y `LLMConfig`.
- `llm_client/config.py`: carga variables de entorno desde `.env`.

## Requisitos

- Python 3.10 o superior
- Acceso a una o más API keys de los proveedores elegidos
- Dependencias de `requirements.txt`

## Instalación

1. Crear un entorno virtual:

```bash
python -m venv .venv
```

2. Activarlo:

- Windows:

```bash
.venv\Scripts\activate
```

- macOS/Linux:

```bash
source .venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

El proyecto lee claves desde variables de entorno o desde un archivo `.env` ubicado en la raíz del proyecto. Para comenzar, copiá `.env.example` como `.env` y completá únicamente las claves de los proveedores que vayas a probar. `.env` está excluido de Git.

Variables esperadas (plantilla disponible en `.env.example`):

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
GOOGLE_API_KEY=
HF_TOKEN=
DEEPSEEK_API_KEY=
```

La carga real se hace en `llm_client/config.py` con `python-dotenv`. `main.py` omite proveedores cuya variable esté vacía y continúa con el siguiente.

## Ejecución

Para probar el flujo sobre varios proveedores:

```bash
python main.py
```

El script itera sobre los proveedores presentes en `PROVEEDORES_A_PROBAR`, ignora los que no tienen clave configurada y continúa con el siguiente. Los errores de configuración o de API se registran por proveedor, sin detener las pruebas restantes. Las llamadas sí requieren claves válidas y acceso a Internet.

## Flujo interno

1. `load_api_keys()` carga las variables desde `.env`.
2. `LLMConfig` valida el provider, modelo, temperatura y API key.
3. `build_llm_client(config)` crea el cliente correcto.
4. `build_prompt_chain(config)` arma la cadena `prompt | model`.
5. La salida se valida contra `EntidadesTecnicas`.

## Modelo de salida

El schema definido en `llm_client/schemas.py` devuelve un objeto con:

- `tecnologias`: lista de tecnologías o frameworks detectados
- `nivel_criticidad`: `baja`, `media` o `alta`
- `resumen_tecnico`: resumen técnico breve

## Observaciones

Algunos proveedores no soportan nativamente `with_structured_output(...)`, por eso `chain.py` incluye un fallback manual para convertir la respuesta del modelo en `EntidadesTecnicas`.

## Autor

Proyecto de prueba y aprendizaje para integrar varios modelos LLM con una interfaz única y reutilizable.

# Instalación: pip install fastapi uvicorn azure-ai-projects azure-identity
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

app = FastAPI()

# Permite que el HTML (Frontend) se comunique con Python (Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datos de tu captura de Azure AI Foundry
ENDPOINT = "https://bot-2026-026-resource.services.ai.azure.com/api/projects/bot_2026_026"
AGENT_ID = "asst_kQUkh2JrCYPhcgn85U8TpttB"

# Cliente de conexión usando tus credenciales de Azure for Students
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=ENDPOINT
)

# Creamos un hilo de conversación persistente
thread = project_client.agents.threads.create()

@app.post("/preguntar")
async def chat_fisica(data: dict):
    pregunta_usuario = data.get("mensaje")
    
    # 1. Enviar el mensaje al hilo del agente
    project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=pregunta_usuario
    )
    
    # 2. Ejecutar el agente para que procese el PDF de física
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=AGENT_ID
    )
    
    # 3. Recuperar la respuesta cuando termine de procesar
    if run.status == "completed":
        messages = project_client.agents.messages.list(thread_id=thread.id)
        # Extraer el texto del último mensaje del asistente
        return {"respuesta": messages.text_messages[-1].text.value}
    else:
        return {"respuesta": f"El agente se detuvo con estado: {run.status}"}

if __name__ == "__main__":
    import uvicorn
    # Lanzar el servidor en el puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

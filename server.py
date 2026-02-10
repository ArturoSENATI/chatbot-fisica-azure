from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import os

app = FastAPI()

# Esto permite que su HTML se conecte al servidor sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración basada en su código de Azure Foundry
ENDPOINT = "https://bot-2026-026-resource.services.ai.azure.com/api/projects/bot_2026_026"
AGENT_ID = "asst_kQDkH2JrCYPhcgn85OBfpft8"

project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=ENDPOINT
)

@app.post("/preguntar")
async def chat_fisica(data: dict):
    pregunta_usuario = data.get("mensaje")
    
    # 1. Creamos un hilo nuevo para cada consulta del alumno
    thread = project_client.agents.threads.create()
    
    # 2. Enviamos la pregunta
    project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=pregunta_usuario
    )
    
    # 3. Procesamos con el Agente de Física
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=AGENT_ID
    )
    
    if run.status == "failed":
        return {"respuesta": f"Lo siento, hubo un error: {run.last_error}"}
    
    # 4. Obtenemos la lista de mensajes en orden para sacar la última respuesta
    messages = project_client.agents.messages.list(
        thread_id=thread.id, 
        order=ListSortOrder.ASCENDING
    )
    
    # 5. Buscamos el último mensaje que envió el asistente
    respuesta_texto = ""
    for msg in messages:
        if msg.role == "assistant" and msg.text_messages:
            respuesta_texto = msg.text_messages[-1].text.value
            
    return {"respuesta": respuesta_texto}

if __name__ == "__main__":
    import uvicorn
    # Render asigna un puerto dinámico, por eso usamos os.environ.get
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

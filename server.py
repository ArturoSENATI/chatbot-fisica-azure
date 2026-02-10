from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import os

app = FastAPI()

# Permite la conexión desde GitHub Pages sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de su proyecto en Azure Foundry
ENDPOINT = "https://bot-2026-026-resource.services.ai.azure.com/api/projects/bot_2026_026"
AGENT_ID = "asst_kQDkH2JrCYPhcgn85OBfpft8"

# Cliente de conexión con las credenciales que ya autorizamos en Azure
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=ENDPOINT
)

@app.post("/preguntar")
async def chat_fisica(data: dict):
    try:
        pregunta_usuario = data.get("mensaje")
        
        # 1. Creamos un hilo de conversación
        thread = project_client.agents.threads.create()
        
        # 2. Enviamos la pregunta de Julia
        project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=pregunta_usuario
        )
        
        # 3. Procesamos con el Agente (Albert FonSesos)
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=AGENT_ID
        )
        
        if run.status == "failed":
            return {"respuesta": f"Lo siento, hubo un error en el procesamiento: {run.last_error}"}
        
        # 4. Obtenemos los mensajes generados
        messages = project_client.agents.messages.list(
            thread_id=thread.id, 
            order=ListSortOrder.ASCENDING
        )
        
        # 5. Lógica mejorada para extraer el texto de la respuesta
        respuesta_texto = "No pude procesar una respuesta, intenta de nuevo."
        for msg in messages:
            if msg.role == "assistant":
                # Intentamos obtener el valor del texto de forma segura
                if hasattr(msg, 'content') and msg.content:
                    # Estructura común en versiones recientes
                    respuesta_texto = msg.content[0].text.value
                elif hasattr(msg, 'text_messages') and msg.text_messages:
                    # Estructura alternativa
                    respuesta_texto = msg.text_messages[-1].text.value
                    
        return {"respuesta": respuesta_texto}

    except Exception as e:
        # Esto nos ayudará a ver el error real en los Logs de Render
        print(f"Error detectado: {str(e)}")
        return {"respuesta": f"¡Rayos! Albert detectó un error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict
import uuid

# Importar el modelo
try:
    from modelo.FisioBotModel import fisiobot_model
    print("✅ Modelo FisioBot cargado correctamente")
except ImportError as e:
    print(f"❌ Error importando modelo: {e}")
    # Crear un mock para desarrollo
    fisiobot_model = None

router = APIRouter(
    prefix="/api/fisiobot",
    tags=["chatbot"]
)

# Almacenamiento simple de conversaciones
chat_sessions = {}

@router.get("/status")
async def chatbot_status():
    """Verifica estado del chatbot"""
    if not fisiobot_model:
        return JSONResponse({
            "status": "error",
            "message": "Modelo no cargado",
            "ready": False
        })
    
    return JSONResponse({
        "status": "active",
        "ready": True,
        "total_questions": len(fisiobot_model.questions) if hasattr(fisiobot_model, 'questions') else 0,
        "version": "1.0",
        "name": "FisioBot"
    })

@router.post("/init")
async def init_chat_session(request: Request):
    """Inicia una nueva sesión de chat"""
    session_id = str(uuid.uuid4())[:8]
    
    # Inicializar sesión
    chat_sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "messages": [],
        "user_info": {}
    }
    
    # Obtener saludo inicial
    if fisiobot_model:
        saludo = fisiobot_model.knowledge_base.get("quick_responses", {}).get("saludo", 
                  "¡Hola! Soy FisioBot, tu asistente virtual.")
    else:
        saludo = "¡Hola! Soy FisioBot. (Modo de emergencia - modelo no cargado)"
    
    return JSONResponse({
        "success": True,
        "session_id": session_id,
        "message": {
            "text": saludo,
            "type": "bot",
            "timestamp": datetime.now().strftime("%H:%M")
        },
        "suggestions": fisiobot_model.get_suggestions() if fisiobot_model else ["Horarios", "Contacto"]
    })

@router.post("/message")
async def process_user_message(request: Request, data: Dict):
    """Procesa un mensaje del usuario"""
    session_id = data.get("session_id")
    user_message = data.get("message", "").strip()
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requerido")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")
    
    # Verificar sesión
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Obtener respuesta del modelo
    if fisiobot_model:
        bot_response = fisiobot_model.find_best_answer(user_message)
    else:
        bot_response = {
            "answer": "El chatbot está en mantenimiento. Por favor llama al 320 2914521.",
            "category": "error",
            "score": 0.0,
            "links": [],
            "id": 0
        }
    
    # Guardar en historial
    chat_sessions[session_id]["messages"].append({
        "type": "user",
        "text": user_message,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    chat_sessions[session_id]["messages"].append({
        "type": "bot",
        "text": bot_response["answer"],
        "category": bot_response.get("category", "default"),
        "timestamp": datetime.now().strftime("%H:%M"),
        "links": bot_response.get("links", [])
    })
    
    # Preparar respuesta
    response_data = {
        "success": True,
        "session_id": session_id,
        "message": {
            "text": bot_response["answer"],
            "type": "bot",
            "timestamp": datetime.now().strftime("%H:%M"),
            "category": bot_response.get("category", "default"),
            "links": bot_response.get("links", []),
            "has_links": len(bot_response.get("links", [])) > 0
        },
        "match_score": bot_response.get("score", 0),
        "suggestions": fisiobot_model.get_suggestions(bot_response.get("category", "default")) if fisiobot_model else []
    }
    
    return JSONResponse(response_data)

@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Obtiene historial de una sesión"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    return JSONResponse({
        "success": True,
        "session_id": session_id,
        "messages": chat_sessions[session_id]["messages"],
        "created_at": chat_sessions[session_id]["created_at"],
        "message_count": len(chat_sessions[session_id]["messages"])
    })

@router.get("/quick-info")
async def get_quick_info():
    """Información rápida para mostrar al inicio"""
    return JSONResponse({
        "success": True,
        "horarios": "Lunes a Viernes: 7:00 AM - 8:00 PM | Sábados: 8:00 AM - 6:00 PM | Domingos: 9:00 AM - 2:00 PM",
        "telefono": "320 2914521",
        "whatsapp": "https://wa.me/573202914521",
        "email": "info@fisiosalud.com",
        "direccion": "Av. Salud #123, Bogotá",
        "servicios_populares": [
            "Masaje Relajante ($35.000)",
            "Terapia de Estiramientos ($40.000)", 
            "Rehabilitación Deportiva ($65.000)"
        ]
    })
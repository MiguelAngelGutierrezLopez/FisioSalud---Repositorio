# type: ignore  # Ignorar warnings de Pylance
import json
import re
import os
import numpy as np  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')

class FisioBotModel:
    def __init__(self, json_path: str = "assets/chatbot_knowledge.json"):
        """Modelo principal del chatbot FisioSalud"""
        print("🤖 Inicializando FisioBot...")
        self.json_path = json_path
        self.knowledge_base = self._load_knowledge_base()
        
        # Inicializar vectorizer para búsqueda inteligente
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=['el', 'la', 'los', 'las', 'de', 'del', 'y', 'o', 'en', 'a', 'que'],
            max_features=1000
        )
        
        self._prepare_search_data()
        print(f"✅ FisioBot listo con {len(self.questions)} preguntas en conocimiento")
    
    def _load_knowledge_base(self) -> Dict:
        """Carga el archivo JSON con el conocimiento"""
        try:
            # Buscar archivo en diferentes ubicaciones posibles
            search_paths = [
                self.json_path,
                os.path.join(os.getcwd(), self.json_path),
                os.path.join(os.getcwd(), "assets", "chatbot_knowledge.json"),
                "chatbot_knowledge.json"
            ]
            
            for path in search_paths:
                if os.path.exists(path):
                    print(f"📂 Cargando conocimiento desde: {path}")
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        item_count = len(data.get("knowledge_base", []))
                        print(f"📊 Base cargada: {item_count} items")
                        return data
            
            print("⚠️ No se encontró el archivo JSON, usando datos mínimos")
            return self._create_minimal_kb()
            
        except Exception as e:
            print(f"❌ Error cargando JSON: {e}")
            return self._create_minimal_kb()
    
    def _create_minimal_kb(self) -> Dict:
        """Crea base de conocimiento mínima de emergencia"""
        return {
            "knowledge_base": [
                {
                    "id": 999,
                    "category": "default",
                    "questions": ["hola", "ayuda", "información"],
                    "answer": "¡Hola! Soy FisioBot. Para información completa, llama al 320 2914521.",
                    "links": ["/contacto"],
                    "keywords": ["hola", "ayuda"]
                }
            ],
            "quick_responses": {
                "saludo": "¡Hola! Soy FisioBot, tu asistente virtual de FisioSalud. ¿En qué puedo ayudarte?",
                "despedida": "¡Gracias por contactar a FisioSalud! Que tengas un excelente día.",
                "no_entiendo": "No entendí completamente. ¿Podrías reformular? O pregúntame sobre horarios, servicios o citas."
            }
        }
    
    def _prepare_search_data(self):
        """Prepara los datos para búsqueda rápida"""
        self.questions = []
        self.answers = []
        
        # Extraer todas las preguntas y respuestas
        for item in self.knowledge_base.get("knowledge_base", []):
            for question in item.get("questions", []):
                self.questions.append(question)
                self.answers.append({
                    "id": item.get("id"),
                    "answer": item.get("answer"),
                    "category": item.get("category"),
                    "links": item.get("links", []),
                    "keywords": item.get("keywords", [])
                })
        
        # Entrenar el vectorizer para búsqueda inteligente
        if self.questions:
            print(f"🔧 Entrenando modelo con {len(self.questions)} preguntas...")
            self.question_vectors = self.vectorizer.fit_transform(self.questions)
        else:
            self.question_vectors = None
            print("⚠️ No hay preguntas para entrenar el modelo")
    
    def normalize_text(self, text: str) -> str:
        """Limpia y normaliza el texto para búsqueda"""
        if not text:
            return ""
        
        text = text.lower().strip()
        # Quitar acentos
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        # Quitar signos de puntuación
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def find_best_answer(self, user_input: str) -> Dict:
        """Encuentra la mejor respuesta para la pregunta del usuario"""
        if not user_input or len(user_input.strip()) < 2:
            return self._get_default_response("Por favor, escribe una pregunta más completa.")
        
        user_input_norm = self.normalize_text(user_input)
        
        # 1. Verificar si es saludo o despedida
        if self._is_greeting(user_input_norm):
            return {
                "answer": self.knowledge_base.get("quick_responses", {}).get("saludo", "¡Hola!"),
                "category": "greeting",
                "score": 1.0,
                "links": [],
                "id": 0
            }
        
        if self._is_farewell(user_input_norm):
            return {
                "answer": self.knowledge_base.get("quick_responses", {}).get("despedida", "¡Hasta luego!"),
                "category": "farewell",
                "score": 1.0,
                "links": [],
                "id": 0
            }
        
        # 2. Búsqueda inteligente con TF-IDF
        best_match = None
        best_score = 0.0
        
        if self.questions and self.question_vectors is not None:
            try:
                user_vector = self.vectorizer.transform([user_input_norm])
                similarities = cosine_similarity(user_vector, self.question_vectors)
                best_idx = np.argmax(similarities)
                best_score = similarities[0][best_idx]
                
                if best_score > 0.2:  # Umbral bajo para mayor cobertura
                    best_match = self.answers[best_idx]
            except Exception as e:
                print(f"⚠️ Error en búsqueda TF-IDF: {e}")
        
        # 3. Si no hay buena coincidencia, buscar por palabras clave
        if not best_match or best_score < 0.3:
            user_words = set(user_input_norm.split())
            for qa in self.answers:
                for keyword in qa.get("keywords", []):
                    if keyword in user_words:
                        return {
                            "answer": qa["answer"],
                            "category": qa["category"],
                            "score": 0.5,
                            "links": qa["links"],
                            "id": qa["id"]
                        }
        
        # 4. Devolver mejor match o respuesta por defecto
        if best_match and best_score > 0.1:
            return {
                "answer": best_match["answer"],
                "category": best_match["category"],
                "score": float(best_score),
                "links": best_match["links"],
                "id": best_match["id"]
            }
        
        return self._get_default_response(user_input)
    
    def _is_greeting(self, text: str) -> bool:
        """Detecta saludos"""
        greetings = ["hola", "buenos", "buenas", "saludos", "hi", "hello"]
        words = text.split()
        return any(greet in words for greet in greetings)
    
    def _is_farewell(self, text: str) -> bool:
        """Detecta despedidas"""
        farewells = ["adiós", "chao", "gracias", "bye", "hasta luego", "nos vemos"]
        words = text.split()
        return any(farewell in words for farewell in farewells)
    
    def _get_default_response(self, user_input: str = "") -> Dict:
        """Respuesta cuando no se entiende"""
        return {
            "answer": self.knowledge_base.get("quick_responses", {}).get("no_entiendo", 
                "No entendí tu pregunta. ¿Podrías intentar de otra forma?\n\nTe sugiero preguntar sobre:\n• Horarios de atención\n• Servicios disponibles\n• Cómo agendar citas\n• Teléfonos de contacto"),
            "category": "default",
            "score": 0.0,
            "links": [],
            "id": 0
        }
    
    def get_suggestions(self, category: str = "default") -> List[str]:
        """Devuelve preguntas sugeridas basadas en categoría"""
        suggestions = {
            "citas_procesos": ["¿Cómo agendo cita?", "¿Puedo cancelar cita?", "¿Necesito registro?"],
            "servicios": ["¿Qué servicios tienen?", "Precios de terapias", "¿Tienen masaje?"],
            "informacion_general": ["Horarios", "Dirección", "Teléfono"],
            "default": ["Horarios", "Cómo agendar", "Teléfono", "Servicios"]
        }
        return suggestions.get(category, suggestions["default"])

# Instancia global para usar en toda la app
fisiobot_model = FisioBotModel()
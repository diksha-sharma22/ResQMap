from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import re
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# Optional: Uncomment to use Hugging Face Transformers (requires: pip install transformers torch)
# from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    timestamp: datetime = None

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
    suggestions: List[str] = []

class SmartResQMapAI:
    """Enhanced AI agent with multiple intelligence backends for ResQMap"""
    
    def __init__(self, agent_type="enhanced_rules"):
        """
        Initialize AI agent with different backends:
        - enhanced_rules: Improved rule-based system (default)
        - huggingface: Use Hugging Face transformers (requires installation)
        - openai: Use OpenAI GPT (requires API key)
        """
        self.agent_type = agent_type
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize based on agent type
        if agent_type == "huggingface":
            self._init_huggingface()
        elif agent_type == "openai":
            self._init_openai()
        else:
            self._init_enhanced_rules()
    
    def _init_huggingface(self):
        """Initialize Hugging Face transformer models"""
        try:
            # Uncomment these lines if you install transformers
            # self.classifier = pipeline("text-classification", 
            #                           model="microsoft/DialoGPT-medium")
            # self.qa_pipeline = pipeline("question-answering",
            #                           model="distilbert-base-cased-distilled-squad")
            print("🤖 Hugging Face models would be loaded here (install transformers first)")
            self.agent_type = "enhanced_rules"  # Fallback
        except Exception as e:
            print(f"⚠️ Hugging Face not available, falling back to enhanced rules: {e}")
            self.agent_type = "enhanced_rules"
    
    def _init_openai(self):
        """Initialize OpenAI GPT"""
        try:
            # Uncomment if you have OpenAI API key
            # import openai
            # openai.api_key = "your-api-key-here"
            print("🤖 OpenAI would be initialized here (add API key)")
            self.agent_type = "enhanced_rules"  # Fallback
        except Exception as e:
            print(f"⚠️ OpenAI not available, falling back to enhanced rules: {e}")
            self.agent_type = "enhanced_rules"
    
    def _init_enhanced_rules(self):
        """Initialize enhanced rule-based system with better NLP"""
        self.knowledge_base = {
            "weather": {
                "keywords": ["weather", "temperature", "rain", "storm", "cyclone", "wind", "humidity", "forecast"],
                "responses": {
                    "current": "I can help you check current weather conditions. Use the weather endpoints or dashboard to get real-time data from HERE API.",
                    "forecast": "Weather forecasts are available for 7 days ahead. Check the forecast page or use /api/weather/forecast endpoint.",
                    "alerts": "Weather alerts show live storm, rain, and cyclone warnings for India. Check /api/weather/india-alerts for current alerts."
                }
            },
            "disaster": {
                "keywords": ["disaster", "emergency", "flood", "earthquake", "cyclone", "evacuation", "rescue", "damage"],
                "responses": {
                    "flood": "For flood information, check the Maps page for flooded areas (blue zones) and evacuation camps. Real-time data is available.",
                    "evacuation": "Evacuation camps and displaced population data are shown on the Maps page with markers. Check active incidents for current status.",
                    "damage": "Infrastructure damage is displayed as red zones on the Maps page. Check the dashboard for damage statistics."
                }
            },
            "maps": {
                "keywords": ["map", "location", "coordinates", "layer", "zone", "area", "incident"],
                "responses": {
                    "layers": "Available map layers: Damaged Zones (red), Flooded Areas (blue), and Displaced Population (markers).",
                    "incidents": "Active incidents show real disaster data for Gujarat (Cyclone), Mumbai (Monsoon Flood), and Assam (River Flood).",
                    "navigation": "Use the Maps page to visualize disaster zones and affected areas across India."
                }
            },
            "api": {
                "keywords": ["api", "endpoint", "data", "integration", "here", "traffic"],
                "responses": {
                    "weather_api": "Weather APIs: /api/weather/current, /api/weather/forecast, /api/weather/india-alerts",
                    "traffic_api": "Traffic APIs: /api/weather/india-traffic, /api/weather/traffic-incidents",
                    "dashboard_api": "Dashboard APIs: /api/dashboard/stats, /api/dashboard/recent-alerts"
                }
            },
            "help": {
                "keywords": ["help", "how", "what", "guide", "tutorial", "support"],
                "responses": {
                    "general": "I'm your ResQMap AI assistant! I can help with weather data, disaster information, maps navigation, and API usage.",
                    "features": "ResQMap features: Live weather alerts, traffic incidents, disaster mapping, evacuation tracking, and real-time data from HERE API.",
                    "getting_started": "Start by checking the Dashboard for overview, then explore Maps for visual data, and Alerts for current warnings."
                }
            }
        }
        
        # Enhanced context memory
        self.conversation_history = []
        self.user_preferences = {}
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extract entities like locations, dates, numbers from message"""
        entities = {
            "locations": [],
            "numbers": [],
            "dates": [],
            "urgency": []
        }
        
        # Location extraction (Indian cities/states)
        locations = ["mumbai", "delhi", "chennai", "kolkata", "bangalore", "hyderabad", 
                    "pune", "ahmedabad", "gujarat", "assam", "kerala", "rajasthan"]
        for loc in locations:
            if loc in message.lower():
                entities["locations"].append(loc.title())
        
        # Number extraction
        import re
        numbers = re.findall(r'\d+', message)
        entities["numbers"] = numbers
        
        # Urgency detection
        urgent_words = ["urgent", "emergency", "critical", "immediate", "help", "asap"]
        for word in urgent_words:
            if word in message.lower():
                entities["urgency"].append(word)
        
        return entities
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Simple semantic similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def analyze_query(self, message: str) -> Dict[str, Any]:
        """Analyze user query and determine intent"""
        message_lower = message.lower()
        
        # Check for specific patterns
        if any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
            return {"intent": "greeting", "confidence": 0.9}
        
        if any(word in message_lower for word in ["thank", "thanks", "bye", "goodbye"]):
            return {"intent": "closing", "confidence": 0.9}
        
        # Check knowledge base categories
        for category, data in self.knowledge_base.items():
            keyword_matches = sum(1 for keyword in data["keywords"] if keyword in message_lower)
            if keyword_matches > 0:
                confidence = min(keyword_matches / len(data["keywords"]), 0.95)
                return {"intent": category, "confidence": confidence, "matches": keyword_matches}
        
        return {"intent": "unknown", "confidence": 0.1}
    
    def generate_response(self, message: str) -> ChatResponse:
        """Generate intelligent response based on user query"""
        # Add to conversation history
        self.conversation_history.append({"user": message, "timestamp": datetime.now()})
        
        # Extract entities for better understanding
        entities = self._extract_entities(message)
        analysis = self.analyze_query(message)
        intent = analysis["intent"]
        confidence = analysis["confidence"]
        
        # Enhanced response generation
        if self.agent_type == "enhanced_rules":
            response_data = self._generate_enhanced_response(message, intent, entities, confidence)
        else:
            response_data = self._generate_basic_response(intent, confidence)
        
        # Add to conversation history
        self.conversation_history.append({"assistant": response_data["response"], "timestamp": datetime.now()})
        
        return ChatResponse(
            response=response_data["response"],
            timestamp=datetime.now(),
            suggestions=response_data["suggestions"]
        )
    
    def _generate_enhanced_response(self, message: str, intent: str, entities: Dict, confidence: float) -> Dict[str, Any]:
        """Generate enhanced contextual responses"""
        suggestions = []
        
        if intent == "greeting":
            response = "Hello! I'm your ResQMap AI assistant. I can help you with weather data, disaster information, maps, and API guidance. What would you like to know?"
            suggestions = ["Show weather alerts", "Explain map layers", "API documentation", "Current disasters"]
        
        elif intent == "closing":
            response = "Thank you for using ResQMap! Stay safe and feel free to ask if you need more help with disaster management."
            suggestions = []
        
        elif intent == "weather":
            # Enhanced weather responses with location awareness
            location_context = ""
            if entities["locations"]:
                location_context = f" for {', '.join(entities['locations'])}"
            
            if "alert" in message.lower():
                response = f"I can show you weather alerts{location_context}. {self.knowledge_base['weather']['responses']['alerts']}"
                suggestions = ["Check current weather", "View 7-day forecast", "Traffic incidents"]
            elif "forecast" in message.lower():
                response = f"Weather forecast{location_context} is available. {self.knowledge_base['weather']['responses']['forecast']}"
                suggestions = ["Current conditions", "Weather alerts", "Severe weather"]
            else:
                response = f"Current weather conditions{location_context} can be checked. {self.knowledge_base['weather']['responses']['current']}"
                suggestions = ["Weather alerts", "7-day forecast", "Severe weather warnings"]
        
        elif intent == "disaster":
            if "flood" in message.lower():
                response = self.knowledge_base["disaster"]["responses"]["flood"]
                suggestions = ["View evacuation camps", "Check damage zones", "Traffic incidents"]
            elif "evacuation" in message.lower():
                response = self.knowledge_base["disaster"]["responses"]["evacuation"]
                suggestions = ["View flooded areas", "Check active incidents", "Weather alerts"]
            else:
                response = self.knowledge_base["disaster"]["responses"]["damage"]
                suggestions = ["View maps", "Check alerts", "Weather conditions"]
        
        elif intent == "maps":
            if "layer" in message.lower():
                response = self.knowledge_base["maps"]["responses"]["layers"]
                suggestions = ["View active incidents", "Check coordinates", "Weather overlay"]
            elif "incident" in message.lower():
                response = self.knowledge_base["maps"]["responses"]["incidents"]
                suggestions = ["View map layers", "Check locations", "Weather data"]
            else:
                response = self.knowledge_base["maps"]["responses"]["navigation"]
                suggestions = ["Map layers", "Active incidents", "Location data"]
        
        elif intent == "api":
            if "weather" in message.lower():
                response = self.knowledge_base["api"]["responses"]["weather_api"]
                suggestions = ["Traffic APIs", "Dashboard APIs", "API documentation"]
            elif "traffic" in message.lower():
                response = self.knowledge_base["api"]["responses"]["traffic_api"]
                suggestions = ["Weather APIs", "Dashboard APIs", "HERE API setup"]
            else:
                response = self.knowledge_base["api"]["responses"]["dashboard_api"]
                suggestions = ["Weather APIs", "Traffic APIs", "API testing"]
        
        elif intent == "help":
            if "feature" in message.lower():
                response = self.knowledge_base["help"]["responses"]["features"]
                suggestions = ["Getting started", "API help", "Map navigation"]
            elif "start" in message.lower():
                response = self.knowledge_base["help"]["responses"]["getting_started"]
                suggestions = ["View dashboard", "Explore maps", "Check alerts"]
            else:
                response = self.knowledge_base["help"]["responses"]["general"]
                suggestions = ["ResQMap features", "Getting started", "API documentation"]
        
        else:
            # Handle unknown queries with context from conversation history
            if entities["urgency"]:
                response = "I understand this seems urgent. For emergency situations, please contact local authorities. I can help you with ResQMap features like weather alerts, disaster maps, or evacuation information."
                suggestions = ["Emergency contacts", "Weather alerts", "Evacuation routes", "Disaster zones"]
            else:
                response = "I understand you're asking about ResQMap. Could you be more specific? I can help with weather data, disaster information, maps, API usage, or general guidance."
                suggestions = ["Weather alerts", "Map layers", "API endpoints", "Disaster information"]
        
        return {"response": response, "suggestions": suggestions}
    
    def _generate_basic_response(self, intent: str, confidence: float) -> Dict[str, Any]:
        """Fallback basic response generation"""
        return {"response": "I'm here to help with ResQMap queries!", "suggestions": ["Ask me anything"]}

# Initialize Smart AI agent with enhanced capabilities
# Options: "enhanced_rules", "huggingface", "openai"
ai_agent = SmartResQMapAI(agent_type="enhanced_rules")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(message: ChatMessage):
    """Chat with ResQMap AI assistant"""
    try:
        if not message.message or not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = ai_agent.generate_response(message.message.strip())
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@router.get("/chat/suggestions")
async def get_chat_suggestions():
    """Get suggested questions for the chatbot"""
    return {
        "suggestions": [
            "What weather alerts are active?",
            "Show me the map layers",
            "How do I use the API?",
            "What disasters are currently happening?",
            "How to check evacuation camps?",
            "Explain traffic incidents",
            "Getting started with ResQMap",
            "What data sources do you use?"
        ]
    }

@router.get("/chat/health")
async def chatbot_health():
    """Health check for chatbot service"""
    return {
        "status": "operational",
        "ai_agent": f"SmartResQMap AI v2.0 ({ai_agent.agent_type})",
        "capabilities": ["weather", "disaster", "maps", "api", "help", "entity_extraction", "context_memory"],
        "conversation_history_length": len(ai_agent.conversation_history),
        "timestamp": datetime.now()
    }

@router.post("/chat/switch-agent")
async def switch_agent(agent_type: str):
    """Switch between different AI agent types"""
    global ai_agent
    
    valid_types = ["enhanced_rules", "huggingface", "openai"]
    if agent_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid agent type. Choose from: {valid_types}")
    
    try:
        ai_agent = SmartResQMapAI(agent_type=agent_type)
        return {
            "status": "success",
            "message": f"Switched to {agent_type} agent",
            "agent_type": ai_agent.agent_type,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch agent: {str(e)}")

@router.get("/chat/agent-info")
async def get_agent_info():
    """Get information about available AI agents"""
    return {
        "current_agent": ai_agent.agent_type,
        "available_agents": {
            "enhanced_rules": {
                "description": "Enhanced rule-based system with entity extraction and context memory",
                "requirements": "None (built-in)",
                "features": ["Intent recognition", "Entity extraction", "Location awareness", "Urgency detection"]
            },
            "huggingface": {
                "description": "Hugging Face Transformers with pre-trained models",
                "requirements": "pip install transformers torch",
                "features": ["Natural language understanding", "Question answering", "Text classification"]
            },
            "openai": {
                "description": "OpenAI GPT models for advanced conversations",
                "requirements": "pip install openai + API key",
                "features": ["Advanced reasoning", "Natural conversations", "Context understanding"]
            }
        },
        "installation_guide": {
            "huggingface": "pip install transformers torch",
            "openai": "pip install openai && set OPENAI_API_KEY=your_key"
        }
    }

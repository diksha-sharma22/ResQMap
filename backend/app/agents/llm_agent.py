import json
from typing import Optional

from groq import Groq

from app.core.config import settings


class GroqToolAgent:
    """LLM-driven agent that picks which ResQMap tool to call based on user query.

    Returns one of: weather_current, weather_forecast, weather_alerts, traffic_incidents
    """

    def __init__(self) -> None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY not configured")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL or "llama-3.1-8b-instant"

    def decide_tool(self, query: str) -> Optional[str]:
        """Return a tool name string or None if undecided."""
        system = (
            "You are a routing agent for a disaster intelligence assistant. "
            "Choose exactly ONE tool that best answers the user's request. "
            "Allowed tools: weather_current, weather_forecast, weather_alerts, traffic_incidents. "
            "Respond ONLY with a JSON object: {\"tool\": <name>} with no extra text."
        )
        user = f"User query: {query}"
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.1,
                max_tokens=64,
            )
            content = resp.choices[0].message.content if resp.choices else ""
            tool = None
            # Try to parse JSON
            try:
                data = json.loads(content)
                tool = data.get("tool")
            except Exception:
                # Fallback: regex search among allowed tools
                for name in [
                    "weather_current",
                    "weather_forecast",
                    "weather_alerts",
                    "traffic_incidents",
                ]:
                    if name in (content or ""):
                        tool = name
                        break
            return tool
        except Exception:
            return None

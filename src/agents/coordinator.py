from typing import Dict, Any, Optional
import time
from google.cloud import aiplatform
from autogen.agentchat.contrib.magentic_one import MagenticOneCoordinator
from ..config import GEMINI_CONFIG, VERIFICATION_CONFIDENCE, COST_THRESHOLD

class MagenticCoordinator:
    """Coordinates price retrieval using Magentic framework with Gemini model."""
    
    def __init__(self):
        """Initialize coordinator with Gemini model."""
        self.model = aiplatform.Model(
            model_name=GEMINI_CONFIG["model"],
            project=aiplatform.initializer.global_config.project,
            location=aiplatform.initializer.global_config.location,
        )
        self.coordinator = MagenticOneCoordinator(
            model=self.model,
            temperature=GEMINI_CONFIG["temperature"],
            max_output_tokens=GEMINI_CONFIG["max_output_tokens"],
            top_p=GEMINI_CONFIG["top_p"],
            top_k=GEMINI_CONFIG["top_k"]
        )
        self.metrics = {
            "requests_processed": 0,
            "total_cost": 0.0,
            "average_latency": 0.0,
            "total_latency": 0.0
        }
    
    async def process_request(self, url: str, download_speed: float, plan_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a price retrieval request using Magentic framework.
        
        Args:
            url: Website URL to scrape
            download_speed: Desired download speed
            plan_name: Optional specific plan name
            
        Returns:
            Dict containing price information and metadata
        """
        start_time = time.time()
        
        try:
            # Prepare the prompt for the model
            prompt = self._build_prompt(url, download_speed, plan_name)
            
            # Get response from model
            response = await self.coordinator.generate(prompt)
            
            # Parse and validate the response
            result = self._parse_response(response)
            
            # Update metrics
            elapsed_time = time.time() - start_time
            self._update_metrics(elapsed_time)
            
            # Check confidence threshold
            if result["confidence"] < VERIFICATION_CONFIDENCE:
                raise ValueError("Confidence below threshold")
                
            # Check cost threshold
            if self.metrics["total_cost"] > COST_THRESHOLD:
                raise ValueError("Cost threshold exceeded")
            
            return result
            
        except Exception as e:
            raise Exception(f"Coordinator processing failed: {str(e)}")
    
    def _build_prompt(self, url: str, download_speed: float, plan_name: Optional[str]) -> str:
        """Build prompt for the model."""
        prompt = (
            f"Extract internet plan pricing information from {url}.\n"
            f"Required download speed: {download_speed} Mbps\n"
        )
        if plan_name:
            prompt += f"Specific plan name: {plan_name}\n"
        
        prompt += (
            "\nFormat the response as JSON with:\n"
            "- price: monthly cost in dollars\n"
            "- confidence: confidence score between 0-1\n"
            "- details: any additional plan information\n"
        )
        return prompt
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate model response."""
        try:
            # Parse JSON response from model
            import json
            parsed = json.loads(response)
            
            # Validate required fields
            if "price" not in parsed or not isinstance(parsed["price"], (int, float)):
                raise ValueError("Invalid or missing price in response")
            
            if "confidence" not in parsed or not isinstance(parsed["confidence"], (int, float)):
                parsed["confidence"] = 0.0
                
            if "details" not in parsed or not isinstance(parsed["details"], dict):
                parsed["details"] = {}
                
            result = {
                "price": float(parsed["price"]),
                "confidence": float(parsed["confidence"]),
                "details": parsed["details"]
            }
            
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse model response: {str(e)}")
    
    def _update_metrics(self, elapsed_time: float):
        """Update performance metrics."""
        self.metrics["requests_processed"] += 1
        self.metrics["total_latency"] += elapsed_time
        self.metrics["average_latency"] = (
            self.metrics["total_latency"] / self.metrics["requests_processed"]
        )
        # TODO: Implement actual cost calculation
        self.metrics["total_cost"] += 0.001  # Placeholder cost per request
        
    def monitor_performance(self) -> Dict[str, Any]:
        """Get coordinator performance metrics."""
        return self.metrics

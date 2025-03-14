from typing import Dict, Any, Optional
import time
from autogen_ext.agents import MultimodalWebSurfer
from bs4 import BeautifulSoup
import requests
from ..config import VERIFICATION_CONFIDENCE

class WebSurferAgent:
    """Agent for web interaction and content processing using MultimodalWebSurfer."""
    
    def __init__(self):
        """Initialize web surfer agent."""
        self.web_surfer = MultimodalWebSurfer()
        self.metrics = {
            "pages_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "average_load_time": 0.0,
            "total_load_time": 0.0
        }
        
    async def process_content(self, url: str, download_speed: Optional[float] = None, plan_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process web content from given URL.
        
        Args:
            url: Website URL to process
            download_speed: Optional download speed to filter plans
            plan_name: Optional specific plan name to look for
            
        Returns:
            Dict containing processed content and metadata
        """
        start_time = time.time()
        
        try:
            # First try with MultimodalWebSurfer
            content = await self.web_surfer.browse(url)
            
            # If that fails, fallback to basic requests
            if not content:
                response = requests.get(url)
                response.raise_for_status()
                content = response.text
                
            # Parse the content
            data = await self._extract_plan_information(content, download_speed, plan_name)
            
            # Update metrics
            elapsed_time = time.time() - start_time
            self._update_metrics(elapsed_time, success=True)
            
            return data
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, success=False)
            raise Exception(f"Web content processing failed: {str(e)}")
            
    async def _extract_plan_information(self, content: str, download_speed: Optional[float], plan_name: Optional[str]) -> Dict[str, Any]:
        """Extract relevant plan information from content."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract all potential plan elements
            plans = []
            
            # Look for common plan container patterns
            plan_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(
                term in x.lower() for term in ['plan', 'package', 'pricing', 'subscription']
            ))
            
            for container in plan_containers:
                plan = {
                    "name": self._extract_text(container, ['h1', 'h2', 'h3', '.plan-name', '.title']),
                    "price": self._extract_price(container),
                    "speed": self._extract_speed(container),
                    "details": self._extract_details(container)
                }
                plans.append(plan)
            
            # Filter plans based on criteria
            matching_plans = self._filter_plans(plans, download_speed, plan_name)
            
            if not matching_plans:
                return {
                    "error": "No matching plans found",
                    "confidence": 0.0,
                    "extracted_plans": plans
                }
            
            # Return best matching plan
            best_match = matching_plans[0]
            return {
                "name": best_match["name"],
                "price": best_match["price"],
                "speed": best_match["speed"],
                "details": best_match["details"],
                "confidence": self._calculate_confidence(best_match)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to extract plan information: {str(e)}")
            
    def _extract_text(self, container, selectors) -> Optional[str]:
        """Extract text using multiple possible selectors."""
        for selector in selectors:
            element = container.find(selector) if selector in ['h1', 'h2', 'h3'] else container.select_one(selector)
            if element and element.text.strip():
                return element.text.strip()
        return None
        
    def _extract_price(self, container) -> Optional[float]:
        """Extract price from container."""
        price_patterns = [
            r'\$\d+\.?\d*',  # $XX.XX
            r'\d+\.?\d*\s*/\s*mo',  # XX.XX /mo
            r'\d+\.?\d*\s*per\s*month'  # XX.XX per month
        ]
        
        # TODO: Implement price extraction logic
        return None
        
    def _extract_speed(self, container) -> Optional[float]:
        """Extract speed from container."""
        speed_patterns = [
            r'(\d+\.?\d*)\s*mbps',
            r'(\d+\.?\d*)\s*mb/s',
            r'(\d+\.?\d*)\s*mbit'
        ]
        
        # TODO: Implement speed extraction logic
        return None
        
    def _extract_details(self, container) -> Dict[str, Any]:
        """Extract additional plan details."""
        details = {}
        # TODO: Implement details extraction logic
        return details
        
    def _filter_plans(self, plans: list, download_speed: Optional[float], plan_name: Optional[str]) -> list:
        """Filter plans based on criteria."""
        matching_plans = plans.copy()
        
        if download_speed:
            matching_plans = [
                plan for plan in matching_plans
                if plan["speed"] and abs(plan["speed"] - download_speed) / download_speed <= 0.1
            ]
            
        if plan_name:
            matching_plans = [
                plan for plan in matching_plans
                if plan["name"] and plan_name.lower() in plan["name"].lower()
            ]
            
        return sorted(matching_plans, key=lambda x: self._calculate_confidence(x), reverse=True)
        
    def _calculate_confidence(self, plan: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted plan."""
        score = 0.0
        
        # Basic validation
        if plan["name"]:
            score += 0.2
        if plan["price"]:
            score += 0.3
        if plan["speed"]:
            score += 0.3
        if plan["details"]:
            score += 0.2
            
        return min(score, 1.0)
        
    def _update_metrics(self, elapsed_time: float, success: bool):
        """Update performance metrics."""
        self.metrics["pages_processed"] += 1
        if success:
            self.metrics["successful_extractions"] += 1
        else:
            self.metrics["failed_extractions"] += 1
            
        self.metrics["total_load_time"] += elapsed_time
        self.metrics["average_load_time"] = (
            self.metrics["total_load_time"] / self.metrics["pages_processed"]
        )
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get web surfer performance metrics."""
        return self.metrics

from typing import Dict, Any, Optional, List
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import asyncio
import requests
from bs4 import BeautifulSoup
from ..config import MAX_AGENTS, VERIFICATION_CONFIDENCE

class ScraperAgent:
    """Individual scraper agent for fallback system."""
    
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.metrics = {
            "requests_handled": 0,
            "successful_extractions": 0,
            "failed_extractions": 0
        }
        
    async def extract_price(self, url: str, download_speed: float, plan_name: Optional[str] = None) -> Dict[str, Any]:
        """Extract price information from URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple extraction based on common patterns
            price = self._find_price(soup, download_speed, plan_name)
            
            self.metrics["requests_handled"] += 1
            if price:
                self.metrics["successful_extractions"] += 1
                return {
                    "price": price,
                    "confidence": 0.7,  # Lower confidence for fallback
                    "agent_id": self.agent_id,
                    "details": {"extraction_method": "fallback_pattern_matching"}
                }
            else:
                self.metrics["failed_extractions"] += 1
                return {
                    "error": "No matching price found",
                    "confidence": 0.0,
                    "agent_id": self.agent_id
                }
                
        except Exception as e:
            self.metrics["failed_extractions"] += 1
            raise Exception(f"Agent {self.agent_id} extraction failed: {str(e)}")
            
    def _find_price(self, soup: BeautifulSoup, download_speed: float, plan_name: Optional[str]) -> Optional[float]:
        """Find price in soup based on criteria."""
        try:
            # Look for plan containers
            plans = soup.find_all(['div', 'section'], class_=lambda x: x and any(
                term in str(x).lower() for term in ['plan', 'package', 'pricing']
            ))
            
            for plan in plans:
                # Check if plan matches criteria
                if plan_name and plan_name.lower() not in str(plan).lower():
                    continue
                    
                speed_text = plan.find(string=lambda x: 'mbps' in str(x).lower())
                if speed_text:
                    try:
                        found_speed = float(''.join(filter(str.isdigit, speed_text)))
                        if abs(found_speed - download_speed) / download_speed > 0.1:
                            continue
                    except:
                        continue
                
                # Look for price
                price_text = plan.find(string=lambda x: '$' in str(x))
                if price_text:
                    try:
                        return float(''.join(filter(str.isdigit, price_text)))
                    except:
                        continue
            
            return None
            
        except Exception:
            return None

class RoundRobinDistributor:
    """Fallback system using round-robin distribution of scraper agents."""
    
    def __init__(self):
        """Initialize distributor with pool of agents."""
        self.agents = [ScraperAgent(i) for i in range(MAX_AGENTS)]
        self.current_agent = 0
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
        self.executor = ThreadPoolExecutor(max_workers=MAX_AGENTS)
        
    async def process_request(self, url: str, download_speed: float, plan_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process request using round-robin distribution among agents.
        
        Args:
            url: Website URL to scrape
            download_speed: Desired download speed
            plan_name: Optional specific plan name
            
        Returns:
            Dict containing price information and metadata
        """
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # Get next agent in rotation
            agent = self.agents[self.current_agent]
            self.current_agent = (self.current_agent + 1) % len(self.agents)
            
            # Process with selected agent
            result = await agent.extract_price(url, download_speed, plan_name)
            
            # Update metrics
            elapsed_time = time.time() - start_time
            self._update_metrics(elapsed_time, success="error" not in result)
            
            if "error" in result:
                # Try parallel processing with remaining agents
                results = await self._parallel_process(url, download_speed, plan_name, exclude_agent=agent.agent_id)
                if results:
                    return max(results, key=lambda x: x.get("confidence", 0))
                raise Exception("All agents failed to extract price")
                
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self._update_metrics(elapsed_time, success=False)
            raise Exception(f"Fallback processing failed: {str(e)}")
            
    async def _parallel_process(self, url: str, download_speed: float, plan_name: Optional[str], exclude_agent: int) -> List[Dict[str, Any]]:
        """Process request with multiple agents in parallel."""
        agents = [a for a in self.agents if a.agent_id != exclude_agent]
        
        # Create tasks for each agent
        tasks = []
        for agent in agents:
            task = asyncio.create_task(agent.extract_price(url, download_speed, plan_name))
            tasks.append(task)
            
        # Wait for all tasks to complete
        results = []
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                if "error" not in result:
                    results.append(result)
            except:
                continue
                
        return results
        
    def _update_metrics(self, elapsed_time: float, success: bool):
        """Update performance metrics."""
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            
        self.metrics["total_response_time"] += elapsed_time
        self.metrics["average_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["total_requests"]
        )
        
    def get_system_load(self) -> Dict[str, Any]:
        """Get system load and performance metrics."""
        return {
            **self.metrics,
            "agent_metrics": [agent.metrics for agent in self.agents]
        }

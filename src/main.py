from typing import Dict, Any, Optional
from .agents.coordinator import MagenticCoordinator
from .agents.web_surfer import WebSurferAgent
from .agents.fallback import RoundRobinDistributor

class PriceRetriever:
    """Main entry point for internet plan price retrieval."""
    
    def __init__(self):
        self.coordinator = MagenticCoordinator()
        self.web_surfer = WebSurferAgent()
        self.fallback = RoundRobinDistributor()
        
    async def get_plan_price(self,
                           url: str,
                           download_speed: float,
                           plan_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve and verify internet plan price.
        
        Args:
            url: Website URL to scrape
            download_speed: Desired download speed
            plan_name: Optional specific plan name
            
        Returns:
            Dict containing:
                - price: Verified price
                - confidence: Confidence score
                - source: Source of price (coordinator/fallback)
                - computational_cost: Cost of operation
                - details: Additional plan information
        """
        try:
            # Try primary coordinator first
            result = await self.coordinator.process_request(
                url=url,
                download_speed=download_speed,
                plan_name=plan_name
            )
            result["source"] = "coordinator"
            return result
        except Exception as e:
            # Fall back to round-robin system
            result = await self.fallback.process_request(
                url=url,
                download_speed=download_speed,
                plan_name=plan_name
            )
            result["source"] = "fallback"
            return result
            
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and metrics."""
        return {
            "coordinator_metrics": self.coordinator.monitor_performance(),
            "web_surfer_metrics": self.web_surfer.get_performance_metrics(),
            "fallback_metrics": self.fallback.get_system_load()
        }

if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        if len(sys.argv) < 3:
            print("Usage: python main.py <url> <download_speed> [plan_name]")
            sys.exit(1)
            
        url = sys.argv[1]
        download_speed = float(sys.argv[2])
        plan_name = sys.argv[3] if len(sys.argv) > 3 else None
        
        retriever = PriceRetriever()
        result = await retriever.get_plan_price(url, download_speed, plan_name)
        print(f"Result: {result}")
        
    asyncio.run(main())

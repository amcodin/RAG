from typing import Dict, Any, List, Optional
from collections import deque
import autogen
from autogen.agentchat import Agent
from ..config import GEMINI_CONFIG, MAX_AGENTS

class RoundRobinDistributor:
    """Fallback system with round-robin task distribution."""
    
    def __init__(self):
        self.agents = self._create_agent_pool()
        self.agent_queue = deque(self.agents)  # For round-robin distribution
        self.current_tasks: Dict[str, Agent] = {}
        
    def _create_agent_pool(self) -> List[Agent]:
        """Create pool of fallback agents."""
        agents = []
        for i in range(MAX_AGENTS):
            agent = autogen.agentchat.ConversableAgent(
                name=f"fallback_agent_{i}",
                llm_config={
                    "config_list": [GEMINI_CONFIG],
                    "temperature": GEMINI_CONFIG["temperature"]
                }
            )
            agents.append(agent)
        return agents
        
    def get_next_agent(self) -> Agent:
        """Get next available agent using round-robin."""
        next_agent = self.agent_queue[0]
        self.agent_queue.rotate(-1)  # Move used agent to end
        return next_agent
        
    async def process_request(self,
                            url: str,
                            download_speed: float,
                            plan_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process request using fallback system.
        
        Args:
            url: Website URL to scrape
            download_speed: Desired download speed
            plan_name: Optional specific plan name
            
        Returns:
            Dict containing price information and verification details
        """
        agent = self.get_next_agent()
        task_id = f"{url}_{download_speed}_{plan_name}"
        self.current_tasks[task_id] = agent
        
        try:
            # TODO: Implement fallback processing logic
            raise NotImplementedError("Fallback processing to be implemented")
        finally:
            # Cleanup task tracking
            self.current_tasks.pop(task_id, None)
            
    def get_agent_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for each agent."""
        stats = {}
        for agent in self.agents:
            stats[agent.name] = {
                "tasks_completed": 0,
                "success_rate": 0.0,
                "average_time": 0.0
            }
        return stats
        
    def get_system_load(self) -> Dict[str, Any]:
        """Get current system load information."""
        return {
            "active_tasks": len(self.current_tasks),
            "queue_length": len(self.agent_queue),
            "agents_available": MAX_AGENTS - len(self.current_tasks)
        }

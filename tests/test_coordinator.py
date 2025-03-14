import pytest
import json
from src.agents.coordinator import MagenticCoordinator

@pytest.fixture
def coordinator():
    return MagenticCoordinator()

def test_build_prompt(coordinator):
    """Test prompt building with different parameters."""
    # Test with required parameters
    url = "https://example.com"
    speed = 100.0
    prompt = coordinator._build_prompt(url, speed, None)
    assert url in prompt
    assert str(speed) in prompt
    assert "JSON" in prompt
    
    # Test with optional plan name
    plan_name = "Premium Plan"
    prompt = coordinator._build_prompt(url, speed, plan_name)
    assert plan_name in prompt

def test_parse_valid_response(coordinator):
    """Test parsing valid JSON response."""
    valid_response = json.dumps({
        "price": 89.99,
        "confidence": 0.95,
        "details": {
            "contract_length": "12 months",
            "data_limit": "Unlimited"
        }
    })
    
    result = coordinator._parse_response(valid_response)
    assert result["price"] == 89.99
    assert result["confidence"] == 0.95
    assert "contract_length" in result["details"]
    assert "data_limit" in result["details"]

def test_parse_response_missing_price(coordinator):
    """Test parsing response with missing price."""
    invalid_response = json.dumps({
        "confidence": 0.95,
        "details": {}
    })
    
    with pytest.raises(ValueError, match="Invalid or missing price"):
        coordinator._parse_response(invalid_response)

def test_parse_response_default_values(coordinator):
    """Test parsing response with missing optional fields."""
    minimal_response = json.dumps({
        "price": 89.99
    })
    
    result = coordinator._parse_response(minimal_response)
    assert result["price"] == 89.99
    assert result["confidence"] == 0.0
    assert result["details"] == {}

def test_parse_invalid_json(coordinator):
    """Test parsing invalid JSON response."""
    invalid_json = "Not a JSON string"
    
    with pytest.raises(ValueError, match="Failed to parse model response"):
        coordinator._parse_response(invalid_json)

def test_metrics_update(coordinator):
    """Test metrics updating."""
    initial_requests = coordinator.metrics["requests_processed"]
    initial_latency = coordinator.metrics["total_latency"]
    
    coordinator._update_metrics(1.5)
    
    assert coordinator.metrics["requests_processed"] == initial_requests + 1
    assert coordinator.metrics["total_latency"] == initial_latency + 1.5
    assert coordinator.metrics["average_latency"] == 1.5

@pytest.mark.asyncio
async def test_process_request_validation(coordinator):
    """Test request processing validation."""
    url = "https://example.com"
    speed = 100.0
    
    # Test with mock low confidence response
    coordinator._parse_response = lambda x: {"price": 89.99, "confidence": 0.3, "details": {}}
    
    with pytest.raises(ValueError, match="Confidence below threshold"):
        await coordinator.process_request(url, speed)

def test_monitor_performance(coordinator):
    """Test performance monitoring."""
    metrics = coordinator.monitor_performance()
    assert "requests_processed" in metrics
    assert "total_cost" in metrics
    assert "average_latency" in metrics
    assert "total_latency" in metrics

def test_parse_response_type_validation(coordinator):
    """Test response parsing with incorrect types."""
    invalid_types_response = json.dumps({
        "price": "89.99",  # Price as string instead of number
        "confidence": "high",  # Confidence as string instead of number
        "details": []  # Details as array instead of object
    })
    
    with pytest.raises(ValueError):
        coordinator._parse_response(invalid_types_response)

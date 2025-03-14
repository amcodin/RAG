import pytest
from src.agents.web_surfer import WebSurferAgent
from bs4 import BeautifulSoup

@pytest.fixture
def web_surfer():
    return WebSurferAgent()

@pytest.fixture
def sample_plan_html():
    return """
    <div class="plan">
        <h2 class="plan-name">Premium NBN Plan</h2>
        <div class="price">$89.99 /mo</div>
        <div class="speed">Download speed 100 Mbps</div>
        <ul class="features">
            <li>No contract</li>
            <li>Setup fee $0</li>
            <li>Unlimited data</li>
            <li>Includes free modem</li>
        </ul>
    </div>
    """

@pytest.fixture
def plan_container(sample_plan_html):
    soup = BeautifulSoup(sample_plan_html, 'html.parser')
    return soup.find('div', class_='plan')

def test_extract_price(web_surfer, plan_container):
    """Test price extraction from plan container."""
    price = web_surfer._extract_price(plan_container)
    assert price == 89.99

def test_extract_speed(web_surfer, plan_container):
    """Test speed extraction from plan container."""
    speed = web_surfer._extract_speed(plan_container)
    assert speed == 100.0

def test_extract_details(web_surfer, plan_container):
    """Test details extraction from plan container."""
    details = web_surfer._extract_details(plan_container)
    assert details["contract_length"] == "No contract"
    assert details["setup_fee"] == 0.0
    assert details["data_limit"] == "Unlimited"
    assert "free modem" in details["features"][0].lower()

@pytest.mark.asyncio
async def test_full_content_processing(web_surfer, sample_plan_html):
    """Test full content processing pipeline."""
    result = await web_surfer._extract_plan_information(sample_plan_html, 100.0, None)
    assert result["price"] == 89.99
    assert result["speed"] == 100.0
    assert result["confidence"] > 0.8  # Should have high confidence with all fields present

@pytest.mark.asyncio
async def test_plan_filtering(web_surfer, sample_plan_html):
    """Test plan filtering by speed and name."""
    # Test with matching speed
    result = await web_surfer._extract_plan_information(sample_plan_html, 100.0, None)
    assert result["speed"] == 100.0
    
    # Test with non-matching speed
    result = await web_surfer._extract_plan_information(sample_plan_html, 50.0, None)
    assert "error" in result
    assert result["confidence"] == 0.0
    
    # Test with matching name
    result = await web_surfer._extract_plan_information(sample_plan_html, None, "Premium")
    assert "Premium" in result["name"]
    
    # Test with non-matching name
    result = await web_surfer._extract_plan_information(sample_plan_html, None, "Basic")
    assert "error" in result

def test_confidence_calculation(web_surfer):
    """Test confidence score calculation."""
    # Complete plan should have high confidence
    complete_plan = {
        "name": "Test Plan",
        "price": 89.99,
        "speed": 100.0,
        "details": {"contract": "12 months"}
    }
    assert web_surfer._calculate_confidence(complete_plan) == 1.0
    
    # Partial plan should have lower confidence
    partial_plan = {
        "name": "Test Plan",
        "price": None,
        "speed": 100.0,
        "details": {}
    }
    assert 0.4 <= web_surfer._calculate_confidence(partial_plan) <= 0.6

def test_metrics_tracking(web_surfer):
    """Test metrics tracking functionality."""
    web_surfer._update_metrics(1.0, True)
    assert web_surfer.metrics["pages_processed"] == 1
    assert web_surfer.metrics["successful_extractions"] == 1
    assert web_surfer.metrics["average_load_time"] == 1.0
    
    web_surfer._update_metrics(2.0, False)
    assert web_surfer.metrics["pages_processed"] == 2
    assert web_surfer.metrics["failed_extractions"] == 1
    assert web_surfer.metrics["average_load_time"] == 1.5

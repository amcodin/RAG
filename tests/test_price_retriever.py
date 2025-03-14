import pytest
from src.main import PriceRetriever

test_url = "https://www.aussiebroadband.com.au/internet/nbn-plans/"
test_speed = 100.0

@pytest.fixture
async def price_retriever():
    return PriceRetriever()

@pytest.mark.asyncio
async def test_initialization(price_retriever):
    """Test successful initialization of PriceRetriever."""
    assert price_retriever.coordinator is not None
    assert price_retriever.web_surfer is not None
    assert price_retriever.fallback is not None

@pytest.mark.asyncio
async def test_system_status(price_retriever):
    """Test system status reporting."""
    status = price_retriever.get_system_status()
    assert "coordinator_metrics" in status
    assert "web_surfer_metrics" in status
    assert "fallback_metrics" in status

@pytest.mark.asyncio
async def test_basic_price_retrieval():
    """Test basic price retrieval with mock data."""
    retriever = PriceRetriever()
    test_url = test_url
    test_speed = test_speed
    
    price_info = await retriever.get_plan_price(test_url, test_speed)
    assert isinstance(price_info, dict)
    assert "price" in price_info
    assert "confidence" in price_info
    assert "details" in price_info

@pytest.mark.asyncio
async def test_fallback_system():
    """Test fallback system activation."""
    retriever = PriceRetriever()
    test_url = test_url
    test_speed = test_speed
    
    # Force fallback by simulating coordinator failure
    retriever.coordinator.process_request = lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Simulated coordinator failure"))
    
    price_info = await retriever.get_plan_price(test_url, test_speed)
    assert isinstance(price_info, dict)
    assert "price" in price_info
    assert "confidence" in price_info
    assert "source" in price_info
    assert price_info["source"] == "fallback"

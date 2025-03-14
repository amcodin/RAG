import pytest
from src.main import PriceRetriever

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
    test_url = "https://example.com"
    test_speed = 100.0
    
    # Note: This will raise NotImplementedError until actual implementation
    with pytest.raises(NotImplementedError):
        await retriever.get_plan_price(test_url, test_speed)

@pytest.mark.asyncio
async def test_fallback_system():
    """Test fallback system activation."""
    retriever = PriceRetriever()
    test_url = "https://example.com"
    test_speed = 100.0
    
    # Note: This will raise NotImplementedError until actual implementation
    with pytest.raises(NotImplementedError):
        await retriever.get_plan_price(test_url, test_speed)

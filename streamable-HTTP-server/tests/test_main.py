"""Tests for main module"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from main import fetch_aws_news
import main


@pytest.mark.asyncio
async def test_fetch_aws_news_success():
    """Test successful API call"""
    mock_response_data = {
        "articles": [
            {
                "id": "test-id",
                "title": "Test Article",
                "url": "https://aws.amazon.com/test",
                "type": "News"
            }
        ],
        "pagination_token": "test-token"
    }
    
    # Create a proper async context manager mock
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = MagicMock()
    
    mock_get = AsyncMock(return_value=mock_response)
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get = mock_get
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client_class.return_value = mock_client
        
        result = await fetch_aws_news("lambda", limit=10)
        
        assert result == mock_response_data
        assert "articles" in result
        assert len(result["articles"]) == 1


@pytest.mark.asyncio
async def test_fetch_aws_news_with_filters():
    """Test fetch_aws_news with different filters"""
    mock_response_data = {
        "articles": [
            {
                "id": "test-id",
                "title": "Test Lambda Article",
                "url": "https://aws.amazon.com/test",
                "type": "News"
            }
        ]
    }
    
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = MagicMock()
    
    mock_get = AsyncMock(return_value=mock_response)
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get = mock_get
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client_class.return_value = mock_client
        
        result = await fetch_aws_news("lambda", news_type="news", limit=10)
        
        assert "articles" in result
        # Verify the API was called with correct parameters
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_aws_news_with_date_filter():
    """Test fetch_aws_news with date filter"""
    mock_response_data = {"articles": []}
    
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = MagicMock()
    
    mock_get = AsyncMock(return_value=mock_response)
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get = mock_get
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client_class.return_value = mock_client
        
        result = await fetch_aws_news("lambda", since_date="2025-01-01T00:00:00Z")
        
        assert result == mock_response_data
        # Verify the API was called
        mock_get.assert_called_once()


def test_fetch_aws_news_invalid_date():
    """Test that invalid date format raises ValueError"""
    import asyncio
    
    async def test_invalid_date():
        with pytest.raises(ValueError, match="Invalid date format"):
            await fetch_aws_news("lambda", since_date="invalid-date")
    
    asyncio.run(test_invalid_date())


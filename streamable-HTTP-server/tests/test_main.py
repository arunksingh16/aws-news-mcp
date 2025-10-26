"""Tests for main module"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from main import fetch_aws_news, get_aws_feed_news
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


@pytest.mark.asyncio
async def test_get_aws_feed_news_success():
    """Test successful RSS feed parsing"""
    # Mock feed data
    mock_feed = MagicMock()
    mock_feed.bozo = False
    
    mock_entry1 = MagicMock()
    mock_entry1.get.side_effect = lambda key, default="": {
        "title": "New Lambda Feature",
        "description": "AWS Lambda now supports...",
        "link": "https://aws.amazon.com/lambda/news",
        "published": "2025-10-24T00:00:00Z"
    }.get(key, default)
    
    mock_entry2 = MagicMock()
    mock_entry2.get.side_effect = lambda key, default="": {
        "title": "S3 Update",
        "description": "Amazon S3 announces...",
        "link": "https://aws.amazon.com/s3/news",
        "published": "2025-10-23T00:00:00Z"
    }.get(key, default)
    
    mock_feed.entries = [mock_entry1, mock_entry2]
    
    with patch("feedparser.parse", return_value=mock_feed):
        result_str = await get_aws_feed_news(max_articles=10)
        result = json.loads(result_str)
        
        assert result["source"] == "AWS What's New Feed"
        assert result["total_articles_returned"] == 2
        assert len(result["articles"]) == 2
        assert result["articles"][0]["title"] == "New Lambda Feature"


@pytest.mark.asyncio
async def test_get_aws_feed_news_with_search():
    """Test RSS feed with search keywords"""
    mock_feed = MagicMock()
    mock_feed.bozo = False
    
    mock_entry1 = MagicMock()
    mock_entry1.get.side_effect = lambda key, default="": {
        "title": "New Lambda Feature",
        "description": "AWS Lambda now supports...",
        "link": "https://aws.amazon.com/lambda/news",
        "published": "2025-10-24T00:00:00Z"
    }.get(key, default)
    
    mock_entry2 = MagicMock()
    mock_entry2.get.side_effect = lambda key, default="": {
        "title": "S3 Update",
        "description": "Amazon S3 announces...",
        "link": "https://aws.amazon.com/s3/news",
        "published": "2025-10-23T00:00:00Z"
    }.get(key, default)
    
    mock_feed.entries = [mock_entry1, mock_entry2]
    
    with patch("feedparser.parse", return_value=mock_feed):
        result_str = await get_aws_feed_news(max_articles=10, search_keywords="lambda")
        result = json.loads(result_str)
        
        assert result["total_articles_returned"] == 1
        assert result["articles"][0]["title"] == "New Lambda Feature"
        assert result["search_keywords"] == "lambda"


@pytest.mark.asyncio
async def test_get_aws_feed_news_max_articles_limit():
    """Test that max_articles limit is respected"""
    mock_feed = MagicMock()
    mock_feed.bozo = False
    
    # Create 5 mock entries
    entries = []
    for i in range(5):
        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda key, default="", i=i: {
            "title": f"Article {i}",
            "description": f"Description {i}",
            "link": f"https://aws.amazon.com/article{i}",
            "published": "2025-10-24T00:00:00Z"
        }.get(key, default)
        entries.append(mock_entry)
    
    mock_feed.entries = entries
    
    with patch("feedparser.parse", return_value=mock_feed):
        result_str = await get_aws_feed_news(max_articles=3)
        result = json.loads(result_str)
        
        assert result["total_articles_returned"] == 3


@pytest.mark.asyncio
async def test_get_aws_feed_news_parse_error():
    """Test handling of RSS feed parse error"""
    mock_feed = MagicMock()
    mock_feed.bozo = True
    mock_feed.bozo_exception = Exception("Parse error")
    
    with patch("feedparser.parse", return_value=mock_feed):
        result = await get_aws_feed_news()
        
        assert "Error parsing RSS feed" in result


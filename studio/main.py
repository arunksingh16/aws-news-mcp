#!/usr/bin/env python3

import httpx
import json
import feedparser
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode
from fastmcp import FastMCP

# Optional prompts registration if available alongside this file
try:
    from promptz import register_prompts  # type: ignore
except Exception:  # pragma: no cover
    register_prompts = None  # type: ignore


mcp = FastMCP("AWS News and Blog MCP Server (Studio)")


async def fetch_aws_news(
    topic: str,
    news_type: str = "all",
    include_regional_expansions: bool = False,
    limit: int = 40,
    since_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    base_url = "https://api.aws-news.com/articles"

    params = {
        "page_size": limit,
        "hide_regional_expansions": not include_regional_expansions,
        "search": topic,
    }

    if news_type.lower() == "news":
        params["article_type"] = "news"
    elif news_type.lower() in ("blogs", "blog"):
        params["article_type"] = "blog"

    if since_date:
        # Validate ISO 8601
        datetime.fromisoformat(since_date.replace("Z", "+00:00"))
        params["since"] = since_date

    url = f"{base_url}?{urlencode(params)}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool(
    description="""
        Returns a list of AWS news articles (news and/or blogs) for a topic/service.
    """
)
async def get_aws_news(
    topic: str,
    news_type: str = "all",
    include_regional_expansions: bool = False,
    number_of_results: int = 40,
    since_date: Optional[str] = None,
) -> str:
    try:
        news_articles = await fetch_aws_news(
            topic=topic,
            news_type=news_type,
            include_regional_expansions=include_regional_expansions,
            limit=number_of_results,
            since_date=since_date,
        )
        result = {
            "topic": topic,
            "news_type": news_type,
            "include_regional_expansions": include_regional_expansions,
            "articles": news_articles,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching AWS news: {str(e)}"


@mcp.tool(
    description="""
        Returns only official AWS News announcements for a topic/service.
    """
)
async def get_aws_announcements(
    topic: str,
    include_regional_expansions: bool = False,
    number_of_results: int = 40,
    since_date: Optional[str] = None,
) -> str:
    try:
        articles = await fetch_aws_news(
            topic=topic,
            news_type="news",
            include_regional_expansions=include_regional_expansions,
            limit=number_of_results,
            since_date=since_date,
        )
        result = {
            "topic": topic,
            "news_type": "news",
            "include_regional_expansions": include_regional_expansions,
            "articles": articles,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching AWS announcements: {str(e)}"


@mcp.tool(
    description="""
        Returns only AWS Blog posts for a topic/service.
    """
)
async def get_aws_blogs(
    topic: str,
    number_of_results: int = 40,
    since_date: Optional[str] = None,
) -> str:
    try:
        articles = await fetch_aws_news(
            topic=topic,
            news_type="blogs",
            include_regional_expansions=False,
            limit=number_of_results,
            since_date=since_date,
        )
        result = {
            "topic": topic,
            "news_type": "blogs",
            "include_regional_expansions": False,
            "articles": articles,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching AWS blogs: {str(e)}"


@mcp.tool(
    description="""
        Fetch the latest AWS announcements from the official What's New RSS feed.
    """
)
async def get_aws_feed_news(
    max_articles: int = 10,
    search_keywords: Optional[str] = None,
) -> str:
    try:
        feed_url = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            return f"Error parsing RSS feed: {feed.bozo_exception}"

        articles: List[Dict[str, Any]] = []
        for entry in feed.entries:
            title = entry.get("title", "")
            description = entry.get("description", "")
            link = entry.get("link", "")
            published = entry.get("published", "")

            if search_keywords:
                search_lower = search_keywords.lower()
                if search_lower not in title.lower() and search_lower not in description.lower():
                    continue

            article_info: Dict[str, Any] = {
                "title": title,
                "description": description,
                "url": link,
                "published_date": published,
            }
            if hasattr(entry, "tags"):
                article_info["tags"] = [tag.term for tag in entry.tags]
            articles.append(article_info)
            if len(articles) >= max_articles:
                break

        result = {
            "source": "AWS What's New Feed",
            "feed_url": feed_url,
            "total_articles_returned": len(articles),
            "search_keywords": search_keywords,
            "articles": articles,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching AWS feed: {str(e)}"


if register_prompts:
    register_prompts(mcp)  # type: ignore


if __name__ == "__main__":
    mcp.run(transport="stdio")



# AWS News & Blog MCP Server

A FastMCP server that provides AI assistants with access to AWS news, announcements, and blog posts from the public AWS API (api.aws-news.com). This server enables LLMs to fetch and analyze the latest AWS updates, feature releases, and regional expansions.

## Features

- 🎯 **1 Tool**: `get_aws_news` - Fetch AWS news and blogs with flexible filtering
- 🎨 **7 Prompts**: Pre-built prompt templates for common queries
- 🔍 **Flexible Search**: Filter by service, date, content type, and regional expansions
- 🌐 **Health Endpoint**: Built-in health check for monitoring
- ✅ **Fully Tested**: Comprehensive test suite with pytest

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running Locally

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Server will start on `http://0.0.0.0:8000`

### Using Docker

```bash
# Build the image
docker build -t aws-news-mcp .

# Run the container
docker run -p 8000:8000 aws-news-mcp
```

## Core Concepts

### Understanding `promptz.py`

MCP Prompts are **discoverable templates** that help LLMs know what questions they can ask. Think of them as "suggested queries" or "shortcuts" that guide the AI assistant.

When an LLM connects to your MCP server, it can discover available prompts:

```
LLM: "What prompts are available?"
MCP Server: 
  - aws_recent_updates (Get recent AWS updates...)
  - aws_latest_blogs (Get blog posts...)
  - aws_latest_announcements (Get official announcements...)
  - ... and 4 more
```

When a user asks something vague, the LLM can use a prompt template:

```
User: "What's happening with Lambda?"
LLM: [Sees aws_recent_updates and uses it]
     → Calls aws_recent_updates("Lambda", days=30)
     → Gets: "Call get_aws_news with: topic='Lambda', news_type='all', 
             since_date='2025-09-26T12:34:56Z'"
     → Then executes get_aws_news tool with those exact parameters
```

### Real Example Flow

```python
# User says: "Any new Lambda features?"

# Step 1: LLM discovers your prompts
Available prompts:
  - aws_recent_updates(service, days=30)
  - aws_latest_blogs(service, days=14)
  - aws_latest_announcements(service, days=30)

# Step 2: LLM selects aws_recent_updates
aws_recent_updates(service="Lambda", days=30)

# Step 3: Prompt returns actionable instruction
→ "Call get_aws_news with: topic='lambda', news_type='all', 
   since_date='2025-09-26T12:34:56Z', number_of_results=40"

# Step 4: LLM executes the tool exactly as instructed
get_aws_news(topic="lambda", news_type="all", since_date="2025-09-26T12:34:56Z")

# Step 5: Tool returns actual data
{
  "topic": "lambda",
  "news_type": "all",
  "articles": [
    {
      "id": "019a1830-8167-8431-79fe-d8be483747fd",
      "title": "AWS Lambda increases maximum payload size...",
      "url": "https://aws.amazon.com/about-aws/whats-new/...",
      "type": "News",
      "published_date": "2025-10-24T21:47:03Z"
    }
  ]
}
```

The `@mcp.prompt` decorator tells FastMCP: *"This is a discoverable prompt template that LLMs can use."*

## API Reference

### Tool: `get_aws_news`

Fetch AWS news articles with flexible filtering options.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | string | Yes | - | AWS service or topic to search (e.g., "lambda", "s3", "ec2") |
| `news_type` | string | No | "all" | Content type: "all", "news", or "blogs" |
| `include_regional_expansions` | boolean | No | false | Include regional expansion announcements |
| `number_of_results` | integer | No | 40 | Maximum number of results to return |
| `since_date` | string | No | - | ISO 8601 date to filter from (e.g., "2025-01-01T00:00:00Z") |

**Example Usage:**

```python
# Get all Lambda news and blogs from last 30 days
get_aws_news(topic="lambda", news_type="all")

# Get only S3 blog posts
get_aws_news(topic="s3", news_type="blogs", number_of_results=20)

# Get DynamoDB updates since a specific date
get_aws_news(
    topic="dynamodb",
    since_date="2025-01-01T00:00:00Z",
    include_regional_expansions=True
)
```

**Example Response:**

```json
{
  "topic": "lambda",
  "news_type": "all",
  "include_regional_expansions": false,
  "articles": [
    {
      "id": "019a1830-8167-8431-79fe-d8be483747fd",
      "url": "https://aws.amazon.com/about-aws/whats-new/2025/10/aws-lambda-payload-size-256-kb-1-mb-invocations/",
      "title": "AWS Lambda increases maximum payload size from 256 KB to 1 MB for asynchronous invocations",
      "slug": "2025-10-24-aws-lambda-increases-maximum-payload-size...",
      "external_id": "whats-new-v2#launch-pf3vpwtdyh5ourngrtygqp",
      "published_date": "2025-10-24T21:47:03.399128Z",
      "type": "News",
      "popular": true,
      "main_category": null,
      "is_regional_expansion": false
    }
  ],
  "pagination_token": "019a0d77-c0a7-ef6f-8b2d-0626373a4ad8"
}
```

## Available Prompts

The server includes 7 pre-built prompts to guide LLMs in making effective queries:

### 1. `aws_recent_updates`
Get recent AWS updates (both news and blogs) for any service.

**Parameters:**
- `service` (str): Any AWS service name (e.g., "lambda", "s3", "ec2")
- `days` (int): Number of days to look back (default: 30)

**Use cases:**
- "What's new with Lambda?"
- "Recent S3 updates"
- "Show me DynamoDB changes in the last 7 days"

### 2. `aws_latest_blogs`
Get only AWS blog posts for any service.

**Parameters:**
- `service` (str): Any AWS service name
- `days` (int): Number of days to look back (default: 14)

**Use cases:**
- "Lambda blogs from last 2 days"
- "Show me recent S3 blog posts"
- "DynamoDB blogs this week"

### 3. `aws_latest_announcements`
Get only official AWS news announcements.

**Parameters:**
- `service` (str): Any AWS service name
- `days` (int): Number of days to look back (default: 30)

**Use cases:**
- "Latest Lambda announcements"
- "EC2 news from last week"
- "What new features were announced for S3?"

### 4. `aws_regional_expansions`
Find AWS regional expansion announcements.

**Parameters:**
- `service` (str): AWS service name or "aws" for all (default: "aws")
- `days` (int): Number of days to look back (default: 90)

**Use cases:**
- "Where is Lambda now available?"
- "New regions for RDS"
- "Regional expansions in the last month"

### 5. `aws_whats_new_today`
Get today's AWS updates.

**Parameters:**
- `service` (str): AWS service name or "aws" for everything (default: "aws")

**Use cases:**
- "What's new in AWS today?"
- "Today's Lambda announcements"
- "Latest updates from today"

### 6. `aws_weekly_digest`
Get a weekly digest of AWS updates.

**Parameters:**
- `service` (str): Any AWS service name
- `weeks` (int): Number of weeks to look back (default: 1)

**Use cases:**
- "Lambda updates this week"
- "What happened with S3 in the last 2 weeks?"
- "Give me a weekly summary for DynamoDB"

### 7. `aws_comprehensive_search`
Comprehensive search across all AWS content.

**Parameters:**
- `service` (str): Any AWS service name
- `days` (int): Number of days to look back (default: 90)
- `include_regional` (bool): Include regional expansions (default: False)

**Use cases:**
- "Everything about Lambda in the last 3 months"
- "Complete S3 coverage including regional news"
- "All DynamoDB content this quarter"

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "aws-news-and-blog-mcp-server"
}
```

### Run Test Suite

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_main.py -v
python -m pytest tests/test_promptz.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

**Test Results:**
- ✅ 4 main.py tests (API functionality)
- ✅ 5 promptz.py tests (Prompt templates)
- ✅ 9 total tests passing

## Project Structure

```
streamable-HTTP-server/
├── main.py              # Main server with tool and health endpoint
├── promptz.py           # Prompt templates for LLMs (7 prompts)
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── README.md           # This file
└── tests/
    ├── __init__.py
    ├── test_main.py    # Tests for main functionality (4 tests)
    └── test_promptz.py # Tests for prompts (5 tests)
```

## Architecture

### Two-Layer Design

The server uses a clean separation of concerns:

**1. `fetch_aws_news()` - Internal HTTP Layer**
- Makes actual HTTP requests to AWS News API
- Handles query parameter construction
- Returns raw JSON data
- Not exposed as an MCP tool

**2. `get_aws_news()` - MCP Tool Layer**
- Exposed as MCP tool (decorated with `@mcp.tool`)
- Calls `fetch_aws_news()` internally
- Adds metadata and formatting
- Handles error responses
- Returns JSON string to LLM

This design enables:
- ✅ Reusability of HTTP logic
- ✅ Easy testing of components
- ✅ Clean error handling
- ✅ Separation of concerns

## Use Cases

- 📰 **Stay Updated**: Get latest announcements for specific AWS services
- 📝 **Research**: Find blog posts and tutorials on AWS topics
- 🌍 **Regional Planning**: Track service availability in new regions
- 📊 **Competitive Analysis**: Monitor AWS product releases and features
- 🤖 **AI Assistants**: Enable LLMs to answer questions about AWS updates
- 📧 **Newsletter Creation**: Gather AWS updates for weekly digests
- 🎓 **Learning**: Discover new AWS features and best practices

## Configuration

The server can be configured by modifying `main.py`:

```python
if __name__ == "__main__":
    mcp.run(
        transport="http",  # Transport protocol
        port=8000,         # Server port
        host="0.0.0.0"     # Bind address
    )
```

### Environment Variables (optional)

You can set these before running:

```bash
export MCP_PORT=8000
export MCP_HOST="0.0.0.0"
```

## Dependencies

**Core:**
- `fastmcp==2.13.0.1` - FastMCP framework for MCP server
- `httpx==0.28.1` - Async HTTP client
- `uvicorn==0.38.0` - ASGI server
- `fastapi==0.120.0` - Web framework

**Development:**
- `pytest==8.3.4` - Testing framework
- `pytest-asyncio==0.24.0` - Async test support

## API Data Source

This server fetches data from the public AWS News API:
- **Base URL**: `https://api.aws-news.com/articles`
- **Documentation**: [AWS News API](https://api.aws-news.com)
- **No authentication required**

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Or use a different port
python main.py  # Edit main.py to change port
```

### Tests failing
```bash
# Ensure you're in the correct directory
cd streamable-HTTP-server

# Reinstall dependencies
pip install -r requirements.txt

# Run tests with verbose output
python -m pytest tests/ -v -s
```

### Import errors
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Verify installations
pip list | grep -E "(fastmcp|httpx|uvicorn|fastapi)"
```

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `python -m pytest tests/ -v`
2. Code follows existing style
3. Add tests for new features
4. Update README with new functionality

## License

See [LICENSE](../LICENSE) file for details.

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [AWS News API](https://api.aws-news.com)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [AWS What's New](https://aws.amazon.com/new/)

---

**Built with ❤️ using FastMCP**

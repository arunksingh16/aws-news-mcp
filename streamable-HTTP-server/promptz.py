"""
Prompts for AWS News and Blog MCP Server
"""

from datetime import datetime, timedelta, UTC
from fastmcp import FastMCP


def register_prompts(mcp: FastMCP):
    """Register all prompts with the MCP server"""

    @mcp.prompt
    def aws_recent_updates(service: str, days: int = 30) -> str:
        """
        Get recent AWS updates (both news and blogs) for any service.
        
        Use this for general questions like:
        - "What's new with Lambda?"
        - "Recent S3 updates"
        - "Show me DynamoDB changes in the last 7 days"
        
        Args:
            service: Any AWS service name (e.g., 'lambda', 's3', 'ec2', 'bedrock')
            days: Number of days to look back (default: 30)
        """
        since_date = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"Call get_aws_news with: topic='{service}', news_type='all', since_date='{since_date}', number_of_results=40"

    @mcp.prompt
    def aws_latest_blogs(service: str, days: int = 14) -> str:
        """
        Get only AWS blog posts for any service.
        
        Use this when specifically asked for blogs:
        - "Lambda blogs from last 2 days"
        - "Show me recent S3 blog posts"
        - "DynamoDB blogs this week"
        
        Args:
            service: Any AWS service name (e.g., 'lambda', 's3', 'rds')
            days: Number of days to look back (default: 14)
        """
        since_date = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"Call get_aws_news with: topic='{service}', news_type='blogs', since_date='{since_date}', number_of_results=40"

    @mcp.prompt
    def aws_latest_announcements(service: str, days: int = 30) -> str:
        """
        Get only official AWS news announcements for any service.
        
        Use this for official announcements:
        - "Latest Lambda announcements"
        - "EC2 news from last week"
        - "What new features were announced for S3?"
        
        Args:
            service: Any AWS service name (e.g., 'lambda', 's3', 'dynamodb')
            days: Number of days to look back (default: 30)
        """
        since_date = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"Call get_aws_news with: topic='{service}', news_type='news', since_date='{since_date}', number_of_results=40"

    @mcp.prompt
    def aws_regional_expansions(service: str = "aws", days: int = 90) -> str:
        """
        Find AWS regional expansion announcements.
        
        Use this for regional availability questions:
        - "Where is Lambda now available?"
        - "New regions for RDS"
        - "Regional expansions in the last month"
        
        Args:
            service: AWS service name or 'aws' for all services (default: 'aws')
            days: Number of days to look back (default: 90)
        """
        since_date = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"Call get_aws_news with: topic='{service}', include_regional_expansions=true, since_date='{since_date}', number_of_results=40"

    @mcp.prompt
    def aws_whats_new_today(service: str = "aws") -> str:
        """
        What's new in AWS today.
        
        Use this for:
        - "What's new in AWS today?"
        - "Today's Lambda announcements"
        - "Latest updates from today"
        
        Args:
            service: AWS service name or 'aws' for everything (default: 'aws')
        """
        today = datetime.now(UTC).strftime("%Y-%m-%dT00:00:00Z")
        return f"Call get_aws_news with: topic='{service}', news_type='all', since_date='{today}', number_of_results=20"

    @mcp.prompt
    def aws_weekly_digest(service: str, weeks: int = 1) -> str:
        """
        Get a weekly digest of AWS updates.
        
        Use this for weekly summaries:
        - "Lambda updates this week"
        - "What happened with S3 in the last 2 weeks?"
        - "Give me a weekly summary for DynamoDB"
        
        Args:
            service: Any AWS service name
            weeks: Number of weeks to look back (default: 1)
        """
        days = weeks * 7
        since_date = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"Call get_aws_news with: topic='{service}', news_type='all', since_date='{since_date}', number_of_results=50"

    @mcp.prompt
    def aws_comprehensive_search(service: str, days: int = 90, include_regional: bool = False) -> str:
        """
        Comprehensive search across all AWS content.
        
        Use this for broad research questions:
        - "Everything about Lambda in the last 3 months"
        - "Complete S3 coverage including regional news"
        - "All DynamoDB content this quarter"
        
        Args:
            service: Any AWS service name
            days: Number of days to look back (default: 90)
            include_regional: Include regional expansions (default: False)
        """
        since_date = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        regional = "true" if include_regional else "false"
        return f"Call get_aws_news with: topic='{service}', news_type='all', since_date='{since_date}', include_regional_expansions={regional}, number_of_results=100"

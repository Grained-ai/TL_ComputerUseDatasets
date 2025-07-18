"""
Bilibili Module

This module provides comprehensive data acquisition capabilities for the Bilibili platform.
It includes list fetching, individual video data extraction, and utility functions.

Main Components:
- BilibiliListFetcher: Bulk video list acquisition
- BilibiliVideoFetcher: Detailed video data extraction
- Data models for validation and serialization
- Utility functions and API client
"""

from .list_fetcher import BilibiliListFetcher
from .video_fetcher import BilibiliVideoFetcher
from .models import (
    VideoMetadata,
    UserInfo,
    VideoStats,
    CommentInfo,
    PlaylistInfo,
    SearchResult,
    APIResponse,
    VideoQuality,
    VideoStatus
)
from .utils import (
    BilibiliAPIClient,
    RateLimiter,
    DataValidator,
    BilibiliUtils,
    APIError,
    ValidationError,
    APIConfig
)

__version__ = "1.0.0"
__author__ = "TL_ComputerUseDatasets Team"

# Main exports
__all__ = [
    # Fetcher classes
    "BilibiliListFetcher",
    "BilibiliVideoFetcher",
    
    # Data models
    "VideoMetadata",
    "UserInfo", 
    "VideoStats",
    "CommentInfo",
    "PlaylistInfo",
    "SearchResult",
    "APIResponse",
    "VideoQuality",
    "VideoStatus",
    
    # Utility classes
    "BilibiliAPIClient",
    "RateLimiter",
    "DataValidator",
    "BilibiliUtils",
    "APIConfig",
    
    # Exceptions
    "APIError",
    "ValidationError"
]

# Convenience functions for quick access
def create_list_fetcher(**kwargs) -> BilibiliListFetcher:
    """
    Create a BilibiliListFetcher instance with optional configuration.
    
    Args:
        **kwargs: Configuration parameters for the fetcher
        
    Returns:
        Configured BilibiliListFetcher instance
    """
    return BilibiliListFetcher(**kwargs)

def create_video_fetcher(**kwargs) -> BilibiliVideoFetcher:
    """
    Create a BilibiliVideoFetcher instance with optional configuration.
    
    Args:
        **kwargs: Configuration parameters for the fetcher
        
    Returns:
        Configured BilibiliVideoFetcher instance
    """
    return BilibiliVideoFetcher(**kwargs)
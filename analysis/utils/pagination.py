"""
Pagination utilities for the analysis app.
"""

import math
from typing import Dict, Any, Optional, List, Union, Tuple, TypeVar, Generic
from django.db.models import QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd

# Type variable for items
T = TypeVar('T')


class PaginatedResponse(Generic[T]):
    """
    Class for paginated responses.
    
    This class provides a standardized format for paginated responses.
    """
    
    def __init__(self, items: List[T], page: int, page_size: int, total: int):
        """
        Initialize the paginated response.
        
        Parameters
        ----------
        items : List[T]
            Items in the current page
        page : int
            Current page number
        page_size : int
            Number of items per page
        total : int
            Total number of items
        """
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total = total
        self.total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the paginated response to a dictionary.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the paginated response
        """
        return {
            'items': self.items,
            'page': self.page,
            'page_size': self.page_size,
            'total': self.total,
            'total_pages': self.total_pages,
            'has_next': self.page < self.total_pages,
            'has_prev': self.page > 1
        }


def paginate_queryset(queryset: QuerySet, page: int = 1, page_size: int = 10) -> PaginatedResponse:
    """
    Paginate a Django queryset.
    
    Parameters
    ----------
    queryset : QuerySet
        Queryset to paginate
    page : int, optional
        Page number, by default 1
    page_size : int, optional
        Number of items per page, by default 10
        
    Returns
    -------
    PaginatedResponse
        Paginated response
    """
    # Create paginator
    paginator = Paginator(queryset, page_size)
    
    # Get page
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
        page = 1
    except EmptyPage:
        # If page is out of range, deliver last page
        page_obj = paginator.page(paginator.num_pages)
        page = paginator.num_pages
    
    # Create paginated response
    return PaginatedResponse(
        items=list(page_obj),
        page=page,
        page_size=page_size,
        total=paginator.count
    )


def paginate_dataframe(df: pd.DataFrame, page: int = 1, page_size: int = 10) -> PaginatedResponse:
    """
    Paginate a pandas DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to paginate
    page : int, optional
        Page number, by default 1
    page_size : int, optional
        Number of items per page, by default 10
        
    Returns
    -------
    PaginatedResponse
        Paginated response
    """
    # Validate page and page_size
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    
    # Calculate start and end indices
    start = (page - 1) * page_size
    end = start + page_size
    
    # Get total number of items
    total = len(df)
    
    # Get items for current page
    if start >= total:
        # If start is out of range, return empty page
        items = []
    else:
        # Get slice of DataFrame
        items = df.iloc[start:end].to_dict('records')
    
    # Create paginated response
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


def paginate_list(items: List[T], page: int = 1, page_size: int = 10) -> PaginatedResponse[T]:
    """
    Paginate a list.
    
    Parameters
    ----------
    items : List[T]
        List to paginate
    page : int, optional
        Page number, by default 1
    page_size : int, optional
        Number of items per page, by default 10
        
    Returns
    -------
    PaginatedResponse[T]
        Paginated response
    """
    # Validate page and page_size
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    
    # Calculate start and end indices
    start = (page - 1) * page_size
    end = start + page_size
    
    # Get total number of items
    total = len(items)
    
    # Get items for current page
    if start >= total:
        # If start is out of range, return empty page
        page_items = []
    else:
        # Get slice of list
        page_items = items[start:end]
    
    # Create paginated response
    return PaginatedResponse(
        items=page_items,
        page=page,
        page_size=page_size,
        total=total
    )

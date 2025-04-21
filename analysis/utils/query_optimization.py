"""
Query optimization utilities for the analysis app.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union, Callable, Type, TypeVar, Tuple
from functools import wraps
from django.db import connection, reset_queries
from django.db.models import QuerySet, Model, Count, Q, F, Prefetch
from django.conf import settings

# Type variable for Django models
T = TypeVar('T', bound=Model)

# Set up logger
logger = logging.getLogger(__name__)


def log_queries(func: Callable) -> Callable:
    """
    Decorator to log database queries executed by a function.
    
    Parameters
    ----------
    func : Callable
        Function to decorate
        
    Returns
    -------
    Callable
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Only log queries in debug mode
        if settings.DEBUG:
            reset_queries()
            start_time = time.time()
            
            # Call the function
            result = func(*args, **kwargs)
            
            # Log queries
            end_time = time.time()
            execution_time = end_time - start_time
            num_queries = len(connection.queries)
            
            logger.debug(
                f"Function {func.__name__} executed {num_queries} queries in {execution_time:.4f} seconds"
            )
            
            # Log individual queries if there are too many
            if num_queries > 10:
                logger.debug("Query summary:")
                queries = {}
                for query in connection.queries:
                    sql = query['sql']
                    if sql in queries:
                        queries[sql] += 1
                    else:
                        queries[sql] = 1
                
                for sql, count in queries.items():
                    if count > 1:
                        logger.debug(f"Query executed {count} times: {sql[:100]}...")
            
            return result
        else:
            # In production, just call the function
            return func(*args, **kwargs)
    
    return wrapper


def optimize_queryset(queryset: QuerySet, select_related: List[str] = None, 
                     prefetch_related: List[str] = None, 
                     annotations: Dict[str, Any] = None,
                     only: List[str] = None,
                     defer: List[str] = None) -> QuerySet:
    """
    Optimize a queryset by adding select_related, prefetch_related, and annotations.
    
    Parameters
    ----------
    queryset : QuerySet
        Queryset to optimize
    select_related : List[str], optional
        Fields to select_related, by default None
    prefetch_related : List[str], optional
        Fields to prefetch_related, by default None
    annotations : Dict[str, Any], optional
        Annotations to add, by default None
    only : List[str], optional
        Fields to include (only), by default None
    defer : List[str], optional
        Fields to exclude (defer), by default None
        
    Returns
    -------
    QuerySet
        Optimized queryset
    """
    # Add select_related
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    # Add prefetch_related
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    # Add annotations
    if annotations:
        queryset = queryset.annotate(**annotations)
    
    # Add only
    if only:
        queryset = queryset.only(*only)
    
    # Add defer
    if defer:
        queryset = queryset.defer(*defer)
    
    return queryset


def get_optimized_queryset(model_class: Type[T], filters: Dict[str, Any] = None,
                          select_related: List[str] = None, 
                          prefetch_related: List[str] = None,
                          annotations: Dict[str, Any] = None,
                          only: List[str] = None,
                          defer: List[str] = None,
                          order_by: List[str] = None) -> QuerySet:
    """
    Get an optimized queryset for a model.
    
    Parameters
    ----------
    model_class : Type[Model]
        Model class
    filters : Dict[str, Any], optional
        Filters to apply, by default None
    select_related : List[str], optional
        Fields to select_related, by default None
    prefetch_related : List[str], optional
        Fields to prefetch_related, by default None
    annotations : Dict[str, Any], optional
        Annotations to add, by default None
    only : List[str], optional
        Fields to include (only), by default None
    defer : List[str], optional
        Fields to exclude (defer), by default None
    order_by : List[str], optional
        Fields to order by, by default None
        
    Returns
    -------
    QuerySet
        Optimized queryset
    """
    # Start with all objects
    queryset = model_class.objects.all()
    
    # Add filters
    if filters:
        queryset = queryset.filter(**filters)
    
    # Optimize queryset
    queryset = optimize_queryset(
        queryset,
        select_related=select_related,
        prefetch_related=prefetch_related,
        annotations=annotations,
        only=only,
        defer=defer
    )
    
    # Add order_by
    if order_by:
        queryset = queryset.order_by(*order_by)
    
    return queryset


def bulk_create_or_update(model_class: Type[T], objects: List[Dict[str, Any]], 
                         unique_fields: List[str], 
                         update_fields: List[str] = None,
                         batch_size: int = 1000) -> Tuple[int, int]:
    """
    Bulk create or update objects.
    
    Parameters
    ----------
    model_class : Type[Model]
        Model class
    objects : List[Dict[str, Any]]
        List of objects to create or update
    unique_fields : List[str]
        Fields that uniquely identify an object
    update_fields : List[str], optional
        Fields to update if object exists, by default None (all fields)
    batch_size : int, optional
        Batch size for bulk operations, by default 1000
        
    Returns
    -------
    Tuple[int, int]
        (created_count, updated_count)
    """
    if not objects:
        return 0, 0
    
    # Get existing objects
    filters = Q()
    for obj in objects:
        obj_filter = Q()
        for field in unique_fields:
            if field in obj:
                obj_filter &= Q(**{field: obj[field]})
        filters |= obj_filter
    
    existing_objects = {
        tuple(getattr(obj, field) for field in unique_fields): obj
        for obj in model_class.objects.filter(filters)
    }
    
    # Separate objects to create and update
    to_create = []
    to_update = []
    
    for obj_dict in objects:
        # Create key for lookup
        key = tuple(obj_dict.get(field) for field in unique_fields)
        
        if key in existing_objects:
            # Object exists, update it
            obj = existing_objects[key]
            
            # Update fields
            fields_to_update = update_fields or obj_dict.keys()
            for field in fields_to_update:
                if field in obj_dict and field not in unique_fields:
                    setattr(obj, field, obj_dict[field])
            
            to_update.append(obj)
        else:
            # Object doesn't exist, create it
            to_create.append(model_class(**obj_dict))
    
    # Bulk create new objects
    created_count = 0
    if to_create:
        created_objects = model_class.objects.bulk_create(to_create, batch_size=batch_size)
        created_count = len(created_objects)
    
    # Bulk update existing objects
    updated_count = 0
    if to_update:
        fields_to_update = update_fields or [f.name for f in model_class._meta.fields 
                                           if f.name not in unique_fields]
        model_class.objects.bulk_update(to_update, fields_to_update, batch_size=batch_size)
        updated_count = len(to_update)
    
    return created_count, updated_count


def chunked_queryset(queryset: QuerySet, chunk_size: int = 1000):
    """
    Split a queryset into chunks to avoid memory issues.
    
    Parameters
    ----------
    queryset : QuerySet
        Queryset to split
    chunk_size : int, optional
        Size of each chunk, by default 1000
        
    Yields
    ------
    QuerySet
        Chunk of the queryset
    """
    # Get primary key name
    pk_name = queryset.model._meta.pk.name
    
    # Get ordered queryset
    queryset = queryset.order_by(pk_name)
    
    # Get first pk
    start_pk = 0
    
    # Get chunks
    while True:
        # Get chunk
        chunk = queryset.filter(**{f"{pk_name}__gt": start_pk})[:chunk_size]
        
        # Check if chunk is empty
        if not chunk:
            break
        
        # Yield chunk
        yield chunk
        
        # Update start_pk
        start_pk = getattr(chunk.last(), pk_name)

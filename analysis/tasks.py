"""
Celery tasks for the analysis app.
"""

import os
import time
import logging
import json
import pandas as pd
import numpy as np
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.db import transaction

from .utils.parsers.factory import ParserFactory
from .utils.validation.validator import Validator
from .utils.visualization.factory import VisualizationFactory
from .utils.cache import disk_cache

logger = logging.getLogger(__name__)


@shared_task
def run_analysis_task(task_id):
    """
    Run an analysis task.

    Parameters
    ----------
    task_id : int
        The ID of the task to run
    """
    from .models import AnalysisTask

    try:
        # Get the task
        task = AnalysisTask.objects.get(id=task_id)

        # Check if the task is already completed or failed
        if task.status in [AnalysisTask.STATUS_COMPLETED, AnalysisTask.STATUS_FAILED]:
            logger.warning(f"Task {task_id} is already completed or failed.")
            return

        # Record the start time
        start_time = time.time()

        # Get related models
        from .models import AnalysisReport, DataCleaningRule, ValidationRule, Visualization

        # Step 1: Load data from data sources
        logger.info(f"Loading data for task {task_id}")
        data_frames = []
        data_sources = task.data_sources.all()

        if not data_sources:
            raise ValueError("No data sources found for this task")

        for task_data_source in data_sources:
            data_source = task_data_source.data_source

            # Skip if file doesn't exist
            if not data_source.file_path or not os.path.exists(data_source.file_path):
                logger.warning(f"File not found for data source {data_source.id}: {data_source.file_path}")
                continue

            # Parse the file
            parser = ParserFactory.get_parser(data_source.file_path)
            df = parser.parse()

            # Add metadata
            df.attrs['source_id'] = data_source.id
            df.attrs['source_name'] = data_source.name

            data_frames.append(df)

        if not data_frames:
            raise ValueError("No valid data sources found for this task")

        # Combine data frames if multiple
        if len(data_frames) == 1:
            combined_df = data_frames[0]
        else:
            # Simple concatenation - in a real app, you'd have more sophisticated merging logic
            combined_df = pd.concat(data_frames, ignore_index=True)

        # Step 2: Apply data cleaning rules
        logger.info(f"Applying cleaning rules for task {task_id}")
        cleaning_rules = task.cleaning_rules.all()
        cleaned_df = combined_df.copy()

        cleaning_results = []
        for rule in cleaning_rules:
            try:
                # Apply the rule based on its type
                if rule.rule_type == DataCleaningRule.TYPE_MISSING_VALUES:
                    # Handle missing values
                    strategy = rule.parameters.get('strategy', 'drop')
                    columns = rule.parameters.get('columns', [])

                    if strategy == 'drop':
                        # Drop rows with missing values
                        if columns:
                            before_count = len(cleaned_df)
                            cleaned_df = cleaned_df.dropna(subset=columns)
                            after_count = len(cleaned_df)
                        else:
                            before_count = len(cleaned_df)
                            cleaned_df = cleaned_df.dropna()
                            after_count = len(cleaned_df)

                        cleaning_results.append({
                            'rule_id': rule.id,
                            'rule_name': rule.name,
                            'rows_affected': before_count - after_count,
                            'success': True
                        })

                    elif strategy == 'fill':
                        # Fill missing values
                        fill_value = rule.parameters.get('fill_value')
                        if columns and fill_value is not None:
                            cleaned_df[columns] = cleaned_df[columns].fillna(fill_value)
                            cleaning_results.append({
                                'rule_id': rule.id,
                                'rule_name': rule.name,
                                'columns_affected': columns,
                                'success': True
                            })

                elif rule.rule_type == DataCleaningRule.TYPE_OUTLIERS:
                    # Handle outliers
                    method = rule.parameters.get('method', 'zscore')
                    columns = rule.parameters.get('columns', [])
                    threshold = rule.parameters.get('threshold', 3.0)

                    if method == 'zscore' and columns:
                        for column in columns:
                            if column in cleaned_df.columns and pd.api.types.is_numeric_dtype(cleaned_df[column]):
                                # Calculate z-scores
                                z_scores = np.abs((cleaned_df[column] - cleaned_df[column].mean()) / cleaned_df[column].std())
                                # Identify outliers
                                outliers = z_scores > threshold
                                # Remove outliers
                                before_count = len(cleaned_df)
                                cleaned_df = cleaned_df[~outliers]
                                after_count = len(cleaned_df)

                                cleaning_results.append({
                                    'rule_id': rule.id,
                                    'rule_name': rule.name,
                                    'column': column,
                                    'outliers_removed': before_count - after_count,
                                    'success': True
                                })

                elif rule.rule_type == DataCleaningRule.TYPE_TRANSFORMATION:
                    # Apply transformations
                    transform_type = rule.parameters.get('transform_type')
                    columns = rule.parameters.get('columns', [])

                    if transform_type and columns:
                        for column in columns:
                            if column in cleaned_df.columns:
                                if transform_type == 'log':
                                    # Log transformation
                                    if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                                        cleaned_df[column] = np.log1p(cleaned_df[column])
                                elif transform_type == 'sqrt':
                                    # Square root transformation
                                    if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                                        cleaned_df[column] = np.sqrt(cleaned_df[column])
                                elif transform_type == 'standardize':
                                    # Standardize
                                    if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                                        cleaned_df[column] = (cleaned_df[column] - cleaned_df[column].mean()) / cleaned_df[column].std()

                                cleaning_results.append({
                                    'rule_id': rule.id,
                                    'rule_name': rule.name,
                                    'column': column,
                                    'transform_type': transform_type,
                                    'success': True
                                })

            except Exception as e:
                logger.error(f"Error applying cleaning rule {rule.id}: {str(e)}")
                cleaning_results.append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'error': str(e),
                    'success': False
                })

        # Step 3: Validate the data
        logger.info(f"Validating data for task {task_id}")
        validation_rules = task.validation_rules.all()

        # Create validator
        validator = Validator(name=f"Task {task_id} Validator")

        # Add rules to validator
        for rule in validation_rules:
            if rule.rule_type == ValidationRule.TYPE_EXPRESSION:
                validator.add_expression_rule(
                    rule_id=str(rule.id),
                    name=rule.name,
                    description=rule.description,
                    expression=rule.expression
                )
            elif rule.rule_type == ValidationRule.TYPE_RANGE:
                validator.add_range_rule(
                    rule_id=str(rule.id),
                    name=rule.name,
                    description=rule.description,
                    column=rule.parameters.get('column'),
                    min_value=rule.parameters.get('min_value'),
                    max_value=rule.parameters.get('max_value'),
                    inclusive=rule.parameters.get('inclusive', True)
                )
            elif rule.rule_type == ValidationRule.TYPE_STATISTICAL:
                validator.add_statistical_rule(
                    rule_id=str(rule.id),
                    name=rule.name,
                    description=rule.description,
                    test_type=rule.parameters.get('test_type'),
                    column=rule.parameters.get('column'),
                    **rule.parameters
                )

        # Run validation
        validation_summary = validator.validate_and_summarize(cleaned_df)

        # Step 4: Generate visualizations
        logger.info(f"Generating visualizations for task {task_id}")
        visualizations_created = []

        # Create basic visualizations based on data types
        numeric_columns = cleaned_df.select_dtypes(include=np.number).columns.tolist()
        categorical_columns = cleaned_df.select_dtypes(include=['object', 'category']).columns.tolist()

        # Create histograms for numeric columns
        for column in numeric_columns[:5]:  # Limit to first 5 columns
            try:
                viz = VisualizationFactory.create('histogram',
                                                column=column,
                                                title=f"Distribution of {column}",
                                                bins=20,
                                                show_statistics=True)
                viz_data = viz.generate(cleaned_df)

                # Save visualization
                viz_obj = Visualization.objects.create(
                    name=f"Histogram of {column}",
                    description=f"Distribution of values in {column}",
                    visualization_type=Visualization.TYPE_HISTOGRAM,
                    configuration={
                        'column': column,
                        'bins': 20,
                        'show_statistics': True
                    },
                    data=viz_data,
                    task=task,
                    created_by=task.created_by
                )

                visualizations_created.append({
                    'id': viz_obj.id,
                    'name': viz_obj.name,
                    'type': viz_obj.visualization_type
                })
            except Exception as e:
                logger.error(f"Error creating histogram for {column}: {str(e)}")

        # Create pie charts for categorical columns
        for column in categorical_columns[:3]:  # Limit to first 3 columns
            try:
                viz = VisualizationFactory.create('pie_chart',
                                                category_column=column,
                                                title=f"Distribution of {column}")
                viz_data = viz.generate(cleaned_df)

                # Save visualization
                viz_obj = Visualization.objects.create(
                    name=f"Pie Chart of {column}",
                    description=f"Distribution of categories in {column}",
                    visualization_type=Visualization.TYPE_PIE,
                    configuration={
                        'category_column': column
                    },
                    data=viz_data,
                    task=task,
                    created_by=task.created_by
                )

                visualizations_created.append({
                    'id': viz_obj.id,
                    'name': viz_obj.name,
                    'type': viz_obj.visualization_type
                })
            except Exception as e:
                logger.error(f"Error creating pie chart for {column}: {str(e)}")

        # Create correlation heatmap if there are multiple numeric columns
        if len(numeric_columns) > 1:
            try:
                viz = VisualizationFactory.create('heatmap',
                                                data_type='correlation',
                                                columns=numeric_columns,
                                                title="Correlation Matrix")
                viz_data = viz.generate(cleaned_df)

                # Save visualization
                viz_obj = Visualization.objects.create(
                    name="Correlation Heatmap",
                    description="Correlation matrix of numeric columns",
                    visualization_type=Visualization.TYPE_HEATMAP,
                    configuration={
                        'data_type': 'correlation',
                        'columns': numeric_columns
                    },
                    data=viz_data,
                    task=task,
                    created_by=task.created_by
                )

                visualizations_created.append({
                    'id': viz_obj.id,
                    'name': viz_obj.name,
                    'type': viz_obj.visualization_type
                })
            except Exception as e:
                logger.error(f"Error creating correlation heatmap: {str(e)}")

        # Step 5: Create a report
        logger.info(f"Creating report for task {task_id}")

        # Create a basic report
        report = AnalysisReport.objects.create(
            title=f"Analysis Report for {task.name}",
            description=f"Automated report generated for task {task.name}",
            format=AnalysisReport.FORMAT_JSON,
            content={
                'task_name': task.name,
                'task_description': task.description,
                'analysis_type': task.analysis_type,
                'data_summary': {
                    'total_rows': len(cleaned_df),
                    'total_columns': len(cleaned_df.columns),
                    'numeric_columns': numeric_columns,
                    'categorical_columns': categorical_columns
                },
                'cleaning_summary': cleaning_results,
                'validation_summary': validation_summary,
                'visualizations': visualizations_created
            },
            task=task,
            created_by=task.created_by
        )

        # Update the task with the results
        task.results = {
            'message': 'Analysis completed successfully.',
            'timestamp': timezone.now().isoformat(),
            'summary': {
                'data_points': len(cleaned_df),
                'validation_rules_passed': validation_summary['passed_rules'],
                'validation_rules_failed': validation_summary['failed_rules'],
                'visualizations_created': len(visualizations_created),
                'report_id': report.id
            }
        }

        # Update the task status
        task.status = AnalysisTask.STATUS_COMPLETED
        task.completed_at = timezone.now()

        # Calculate the execution time
        end_time = time.time()
        task.execution_time = end_time - start_time

        # Save the task
        task.save()

        logger.info(f"Task {task_id} completed successfully.")

    except AnalysisTask.DoesNotExist:
        logger.error(f"Task {task_id} not found.")
    except Exception as e:
        logger.exception(f"Error running task {task_id}: {str(e)}")

        # Update the task with the error
        try:
            task = AnalysisTask.objects.get(id=task_id)
            task.status = AnalysisTask.STATUS_FAILED
            task.error_message = str(e)
            task.save()
        except:
            pass

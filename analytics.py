import json
import os
from datetime import datetime, timezone
import logging
from config import *
from db_manager import DatabaseManager

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, LOG_LEVEL))

class Analytics:
    """
    Handles analytics and feedback data management for the RAG assistant.
    """
    
    @staticmethod
    def initialize_analytics():
        """
        Initialize analytics data structure.
        
        Returns:
            dict: Initial analytics data structure
        """
        logger.info("Initializing analytics data structure")
        return {
            'total_queries': 0,
            'queries': [],
            'feedback': []
        }

    @staticmethod
    def save_feedback(feedback_data: dict):
        """
        Save feedback data to PostgreSQL database.
        
        Args:
            feedback_data (dict): Feedback data to save
        
        Raises:
            Exception: If there's an error saving the feedback
        """
        try:
            logger.info("Saving new feedback to database")
            
            # Format data for database storage
            db_feedback = {
                "question": feedback_data.get("question", ""),
                "response": feedback_data.get("response", ""),
                "evaluation_json": feedback_data.get("evaluation_json", {}),
                "feedback_tags": feedback_data.get("feedback_tags", []),
                "comment": feedback_data.get("comment", "")
            }
            
            # Save to database
            try:
                DatabaseManager.save_feedback(db_feedback)
                logger.info("Feedback saved successfully to database")
            except Exception as db_error:
                logger.error(f"Error saving feedback to database: {db_error}")
                logger.info("Falling back to JSON file storage")
                
                # Fallback to JSON file storage
                # Create feedback directory if it doesn't exist
                os.makedirs(FEEDBACK_DIR, exist_ok=True)
                feedback_file_path = os.path.join(FEEDBACK_DIR, FEEDBACK_FILE)
                
                # Load existing feedback
                existing_feedback = []
                if os.path.exists(feedback_file_path):
                    try:
                        with open(feedback_file_path, "r", encoding='utf-8') as f:
                            existing_feedback = json.load(f)
                            if not isinstance(existing_feedback, list):
                                logger.warning("Existing feedback file is not a list, creating new list")
                                existing_feedback = []
                    except json.JSONDecodeError:
                        logger.warning("Error decoding existing feedback file, creating new list")
                        existing_feedback = []
                
                # Add new feedback
                existing_feedback.append(feedback_data)
                
                # Save updated feedback
                with open(feedback_file_path, "w", encoding='utf-8') as f:
                    json.dump(existing_feedback, f, indent=4)
                
                logger.info("Feedback saved successfully to JSON file")
            
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            raise

    @staticmethod
    def get_feedback_summary():
        """
        Get summary statistics of collected feedback.
        
        Returns:
            dict: Summary statistics of feedback
        """
        try:
            logger.info("Generating feedback summary from database")
            
            try:
                # Try to get summary from database first
                summary = DatabaseManager.get_feedback_summary()
                if summary:
                    logger.info("Feedback summary generated successfully from database")
                    return summary
            except Exception as db_error:
                logger.warning(f"Error getting feedback summary from database: {db_error}")
                logger.info("Falling back to JSON file for feedback summary")
            
            # Fallback to JSON file if database query fails
            feedback_file_path = os.path.join(FEEDBACK_DIR, FEEDBACK_FILE)
            
            if not os.path.exists(feedback_file_path):
                logger.info("No feedback file exists yet")
                return {
                    'total_feedback': 0,
                    'positive_feedback': 0,
                    'negative_feedback': 0,
                    'recent_feedback': []
                }
            
            with open(feedback_file_path, "r", encoding='utf-8') as f:
                feedback_data = json.load(f)
            
            positive_feedback = sum(1 for item in feedback_data if item.get('feedback_type') == 'thumbs_up')
            negative_feedback = sum(1 for item in feedback_data if item.get('feedback_type') == 'thumbs_down')
            
            # Get recent feedback (last 5 entries)
            recent_feedback = sorted(
                feedback_data,
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )[:5]
            
            summary = {
                'total_feedback': len(feedback_data),
                'positive_feedback': positive_feedback,
                'negative_feedback': negative_feedback,
                'recent_feedback': recent_feedback
            }
            
            logger.info("Feedback summary generated successfully from JSON file")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating feedback summary: {e}")
            return {
                'total_feedback': 0,
                'positive_feedback': 0,
                'negative_feedback': 0,
                'recent_feedback': []
            }

    @staticmethod
    def get_query_analytics():
        """
        Analyze query patterns and generate statistics.
        
        Returns:
            dict: Query analytics data
        """
        try:
            logger.info("Generating query analytics from database")
            
            try:
                # Try to get analytics from database first
                analytics = DatabaseManager.get_query_analytics()
                if analytics:
                    logger.info("Query analytics generated successfully from database")
                    return analytics
            except Exception as db_error:
                logger.warning(f"Error getting query analytics from database: {db_error}")
                logger.info("Falling back to JSON file for query analytics")
            
            # Fallback to JSON file if database query fails
            feedback_file_path = os.path.join(FEEDBACK_DIR, FEEDBACK_FILE)
            
            if not os.path.exists(feedback_file_path):
                logger.info("No feedback file exists yet")
                return {
                    'total_queries': 0,
                    'queries_with_feedback': 0,
                    'successful_queries': 0,
                    'recent_queries': []
                }
            
            with open(feedback_file_path, "r", encoding='utf-8') as f:
                feedback_data = json.load(f)
            
            # Get unique queries
            unique_queries = {item.get('question', '') for item in feedback_data if item.get('question')}
            
            # Get successful queries (queries with positive feedback)
            successful_queries = {
                item.get('question', '') for item in feedback_data 
                if item.get('question') and item.get('feedback_type') == 'thumbs_up'
            }
            
            # Get recent queries
            recent_queries = sorted(
                [{'question': item.get('question', ''), 'timestamp': item.get('timestamp', '')} 
                 for item in feedback_data if item.get('question')],
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )[:5]
            
            analytics = {
                'total_queries': len(unique_queries),
                'queries_with_feedback': len(feedback_data),
                'successful_queries': len(successful_queries),
                'recent_queries': recent_queries
            }
            
            logger.info("Query analytics generated successfully from JSON file")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating query analytics: {e}")
            return {
                'total_queries': 0,
                'queries_with_feedback': 0,
                'successful_queries': 0,
                'recent_queries': []
            }

    @staticmethod
    def export_analytics(export_path: str = None):
        """
        Export analytics data to a JSON file.
        
        Args:
            export_path (str, optional): Path to export the analytics data. 
                                       Defaults to 'analytics_export.json' in FEEDBACK_DIR.
        
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            logger.info("Exporting analytics data")
            
            if export_path is None:
                export_path = os.path.join(FEEDBACK_DIR, 'analytics_export.json')
            
            # Gather all analytics data
            analytics_data = {
                'feedback_summary': Analytics.get_feedback_summary(),
                'query_analytics': Analytics.get_query_analytics(),
                'export_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            # Save analytics data
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(analytics_data, f, indent=4)
            
            logger.info(f"Analytics data exported successfully to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return False

    @staticmethod
    def clear_analytics():
        """
        Clear all analytics data (use with caution).
        
        Returns:
            bool: True if clearing successful, False otherwise
        """
        try:
            logger.warning("Attempting to clear all analytics data")
            
            feedback_file_path = os.path.join(FEEDBACK_DIR, FEEDBACK_FILE)
            
            if os.path.exists(feedback_file_path):
                # Create backup before clearing
                backup_path = f"{feedback_file_path}.backup.{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
                os.rename(feedback_file_path, backup_path)
                logger.info(f"Created backup of feedback data at {backup_path}")
            
            # Create new empty feedback file
            with open(feedback_file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            
            logger.info("Analytics data cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing analytics data: {e}")
            return False

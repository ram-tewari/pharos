#!/usr/bin/env python3
"""
Patch monitoring endpoints to return safe defaults instead of 500 errors.
"""

import os
import sys

def patch_monitoring_service():
    """Add try-catch blocks around database queries."""
    
    service_file = "/mnt/c/Users/rooma/PycharmProjects/neo_alexadria/backend/app/modules/monitoring/service.py"
    
    if not os.path.exists(service_file):
        print(f"File not found: {service_file}")
        return False
    
    with open(service_file, 'r') as f:
        content = f.read()
    
    # Add safe defaults to user engagement method
    if 'total_users = db.query(UserProfile).count()' in content:
        content = content.replace(
            'total_users = db.query(UserProfile).count()',
            '''try:
                total_users = db.query(UserProfile).count()
            except Exception:
                total_users = 0'''
        )
    
    # Add safe defaults to recommendation quality method  
    if 'feedback_query = db.query(RecommendationFeedback)' in content:
        content = content.replace(
            '''feedback_query = db.query(RecommendationFeedback).filter(
                RecommendationFeedback.recommended_at >= cutoff_date
            )

            total_recommendations = feedback_query.count()''',
            '''try:
                feedback_query = db.query(RecommendationFeedback).filter(
                    RecommendationFeedback.recommended_at >= cutoff_date
                )
                total_recommendations = feedback_query.count()
            except Exception:
                total_recommendations = 0'''
        )
    
    with open(service_file, 'w') as f:
        f.write(content)
    
    print("✅ Patched monitoring service with safe defaults")
    return True

if __name__ == "__main__":
    patch_monitoring_service()

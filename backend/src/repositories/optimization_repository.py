"""Optimization Repository - Recommendation data access with caching"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json

from src.models import OptimizationRecommendation
from src.config.database import redis_client


class OptimizationRepository:
    """Repository for Optimization Recommendations"""

    CACHE_TTL = 60  # 60 seconds cache

    def __init__(self, db: Session):
        self.db = db

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get data from Redis cache"""
        if not redis_client:
            return None

        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        return None

    def _set_cache(self, key: str, data: Any, ttl: int = CACHE_TTL):
        """Set data in Redis cache"""
        if not redis_client:
            return

        try:
            redis_client.setex(key, ttl, json.dumps(data))
        except Exception:
            pass

    def get_all_recommendations(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all recommendations, optionally filtered by status"""
        cache_key = f"recommendations:all:{status or 'all'}"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        query = self.db.query(OptimizationRecommendation)

        if status:
            query = query.filter(OptimizationRecommendation.status == status)

        recommendations = query.order_by(
            desc(OptimizationRecommendation.savings_monthly)
        ).all()

        result = [rec.to_dict() for rec in recommendations]

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_recommendation_by_id(self, rec_id: int) -> Optional[Dict[str, Any]]:
        """Get single recommendation by ID"""
        cache_key = f"recommendation:{rec_id}"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        rec = self.db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.id == rec_id
        ).first()

        if not rec:
            return None

        result = rec.to_dict()

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_recommendations_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get recommendations by priority"""
        cache_key = f"recommendations:priority:{priority}"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        recommendations = self.db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.priority == priority,
            OptimizationRecommendation.status == "pending"
        ).order_by(desc(OptimizationRecommendation.savings_monthly)).all()

        result = [rec.to_dict() for rec in recommendations]

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_recommendations_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get recommendations by category"""
        cache_key = f"recommendations:category:{category}"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        recommendations = self.db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.category == category,
            OptimizationRecommendation.status == "pending"
        ).order_by(desc(OptimizationRecommendation.savings_monthly)).all()

        result = [rec.to_dict() for rec in recommendations]

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get optimization summary statistics"""
        cache_key = "recommendations:summary"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query all pending recommendations
        recommendations = self.db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.status == "pending"
        ).all()

        total_count = len(recommendations)
        total_monthly_savings = sum(rec.savings_monthly for rec in recommendations)
        total_annual_savings = sum(rec.savings_annual for rec in recommendations)

        # Group by priority
        priority_counts = {}
        priority_savings = {}
        for rec in recommendations:
            priority_counts[rec.priority] = priority_counts.get(rec.priority, 0) + 1
            priority_savings[rec.priority] = priority_savings.get(rec.priority, 0) + rec.savings_monthly

        # Group by category
        category_counts = {}
        category_savings = {}
        for rec in recommendations:
            category_counts[rec.category] = category_counts.get(rec.category, 0) + 1
            category_savings[rec.category] = category_savings.get(rec.category, 0) + rec.savings_monthly

        # Top 5 recommendations by savings
        top_recommendations = sorted(
            recommendations,
            key=lambda x: x.savings_monthly,
            reverse=True
        )[:5]

        result = {
            "totalCount": total_count,
            "totalMonthlySavings": round(total_monthly_savings, 2),
            "totalAnnualSavings": round(total_annual_savings, 2),
            "priorityDistribution": priority_counts,
            "prioritySavings": {k: round(v, 2) for k, v in priority_savings.items()},
            "categoryDistribution": category_counts,
            "categorySavings": {k: round(v, 2) for k, v in category_savings.items()},
            "topRecommendations": [rec.to_dict() for rec in top_recommendations]
        }

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def update_recommendation_status(self, rec_id: int, status: str) -> bool:
        """Update recommendation status"""
        rec = self.db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.id == rec_id
        ).first()

        if not rec:
            return False

        rec.status = status
        self.db.commit()

        # Invalidate cache
        if redis_client:
            try:
                # Clear related caches
                redis_client.delete(f"recommendation:{rec_id}")
                redis_client.delete(f"recommendations:all:*")
                redis_client.delete("recommendations:summary")
            except Exception:
                pass

        return True

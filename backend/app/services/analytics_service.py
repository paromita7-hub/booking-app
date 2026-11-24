"""Analytics and Insights Service.

Calculates KPIs, weekly trends, operational topic distributions, property comparisons,
and actionable operational insights using Sydney timezone calendar weeks.
"""

from datetime import datetime, date, timedelta
import pytz
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.property import Property
from app.models.review import Review
from app.models.review_topic import ReviewTopic
from app.services.analysis_engine import classifier
from app.config import settings


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.tz = pytz.timezone(settings.APP_TIMEZONE)

    def _get_sydney_current_date(self) -> date:
        now_sydney = datetime.now(self.tz)
        return now_sydney.date()

    def _get_weekly_ranges(self, reference_date: date | None = None) -> tuple[date, date, date, date]:
        """Returns (curr_start, curr_end, prev_start, prev_end) for Monday-to-Sunday weeks."""
        ref = reference_date or self._get_sydney_current_date()
        # Monday is weekday 0 in Python
        current_monday = ref - timedelta(days=ref.weekday())
        current_today = ref

        elapsed_days = (current_today - current_monday).days  # e.g., 0 for Mon, 1 for Tue
        prev_monday = current_monday - timedelta(days=7)
        prev_equivalent_day = prev_monday + timedelta(days=elapsed_days)

        return current_monday, current_today, prev_monday, prev_equivalent_day

    def get_kpi_summary(self, property_id: int | None = None) -> dict:
        """Calculates current week vs previous week KPIs."""
        curr_start, curr_end, prev_start, prev_end = self._get_weekly_ranges()

        # Query all reviews
        query = self.db.query(Review)
        if property_id:
            query = query.filter(Review.property_id == property_id)

        all_reviews = query.all()
        total_count = len(all_reviews)

        # Current period reviews
        curr_reviews = [r for r in all_reviews if curr_start <= r.review_date <= curr_end]
        curr_count = len(curr_reviews)
        curr_avg = round(sum(r.rating for r in curr_reviews) / curr_count, 2) if curr_count > 0 else 0.0

        # Previous period reviews (equivalent elapsed period)
        prev_reviews = [r for r in all_reviews if prev_start <= r.review_date <= prev_end]
        prev_count = len(prev_reviews)
        prev_avg = round(sum(r.rating for r in prev_reviews) / prev_count, 2) if prev_count > 0 else 0.0

        rating_change = round(curr_avg - prev_avg, 2) if (curr_count > 0 and prev_count > 0) else 0.0

        # Overall sentiment breakdown (or current period sentiment)
        # We classify review sentiment based on our classifier logic
        pos_count = 0
        neg_count = 0
        mixed_count = 0
        neutral_count = 0

        eval_set = curr_reviews if curr_count > 0 else all_reviews
        eval_total = len(eval_set)

        for r in eval_set:
            analysis = classifier.analyze(r.title, r.positive_text, r.negative_text, r.rating)
            sent = analysis["overall_sentiment"]
            if sent == "Positive":
                pos_count += 1
            elif sent == "Negative":
                neg_count += 1
            elif sent == "Mixed":
                mixed_count += 1
            else:
                neutral_count += 1

        pos_pct = round((pos_count / eval_total) * 100, 1) if eval_total > 0 else 0.0
        neg_pct = round((neg_count / eval_total) * 100, 1) if eval_total > 0 else 0.0
        mixed_pct = round((mixed_count / eval_total) * 100, 1) if eval_total > 0 else 0.0
        neutral_pct = round((neutral_count / eval_total) * 100, 1) if eval_total > 0 else 0.0

        return {
            "current_week_avg_rating": curr_avg,
            "previous_week_avg_rating": prev_avg,
            "rating_change": rating_change,
            "total_reviews_count": total_count,
            "current_week_reviews_count": curr_count,
            "previous_week_reviews_count": prev_count,
            "positive_review_percentage": pos_pct,
            "negative_review_percentage": neg_pct,
            "mixed_review_percentage": mixed_pct,
            "neutral_review_percentage": neutral_pct,
            "period_start": curr_start.isoformat(),
            "period_end": curr_end.isoformat(),
            "previous_period_start": prev_start.isoformat(),
            "previous_period_end": prev_end.isoformat(),
            "timezone": settings.APP_TIMEZONE,
        }

    def get_weekly_trends(self, property_id: int | None = None, weeks_count: int = 8) -> list[dict]:
        """Calculates historical weekly rating and volume trends."""
        ref = self._get_sydney_current_date()
        current_monday = ref - timedelta(days=ref.weekday())

        query = self.db.query(Review)
        if property_id:
            query = query.filter(Review.property_id == property_id)
        reviews = query.all()

        points = []
        for i in range(weeks_count - 1, -1, -1):
            w_start = current_monday - timedelta(days=i * 7)
            w_end = w_start + timedelta(days=6)

            w_reviews = [r for r in reviews if w_start <= r.review_date <= w_end]
            count = len(w_reviews)
            avg_rating = round(sum(r.rating for r in w_reviews) / count, 2) if count > 0 else 0.0

            pos_c = 0
            neg_c = 0
            mixed_c = 0
            for r in w_reviews:
                sent = classifier.analyze(r.title, r.positive_text, r.negative_text, r.rating)["overall_sentiment"]
                if sent == "Positive":
                    pos_c += 1
                elif sent == "Negative":
                    neg_c += 1
                else:
                    mixed_c += 1

            label = f"{w_start.strftime('%d %b')}"
            points.append({
                "week_label": label,
                "week_start": w_start.isoformat(),
                "week_end": w_end.isoformat(),
                "average_rating": avg_rating,
                "total_reviews": count,
                "positive_count": pos_c,
                "negative_count": neg_c,
                "mixed_count": mixed_c,
            })
        return points

    def get_property_comparisons(self) -> list[dict]:
        """Calculates property performance comparisons."""
        properties = self.db.query(Property).all()
        curr_start, curr_end, prev_start, prev_end = self._get_weekly_ranges()

        results = []
        for prop in properties:
            p_reviews = self.db.query(Review).filter(Review.property_id == prop.id).all()
            total = len(p_reviews)
            avg_rating = round(sum(r.rating for r in p_reviews) / total, 2) if total > 0 else 0.0

            # Weekly rating change
            c_revs = [r for r in p_reviews if curr_start <= r.review_date <= curr_end]
            p_revs = [r for r in p_reviews if prev_start <= r.review_date <= prev_end]

            c_avg = sum(r.rating for r in c_revs) / len(c_revs) if c_revs else avg_rating
            p_avg = sum(r.rating for r in p_revs) / len(p_revs) if p_revs else avg_rating
            weekly_change = round(c_avg - p_avg, 2)

            # Sentiment percentages
            pos_c = sum(1 for r in p_reviews if r.rating >= 7.0)
            neg_c = sum(1 for r in p_reviews if r.rating <= 5.5)
            pos_pct = round((pos_c / total) * 100, 1) if total > 0 else 0.0
            neg_pct = round((neg_c / total) * 100, 1) if total > 0 else 0.0

            # Most frequently mentioned negative topic
            neg_topic_query = (
                self.db.query(ReviewTopic.topic, func.count(ReviewTopic.id).label("count"))
                .join(Review, Review.id == ReviewTopic.review_id)
                .filter(Review.property_id == prop.id, ReviewTopic.sentiment.in_(["Negative", "Mixed"]))
                .group_by(ReviewTopic.topic)
                .order_by(desc("count"))
                .first()
            )
            top_neg = neg_topic_query[0] if neg_topic_query else "None"

            results.append({
                "property_id": prop.id,
                "property_name": prop.name,
                "average_rating": avg_rating,
                "total_reviews": total,
                "positive_percentage": pos_pct,
                "negative_percentage": neg_pct,
                "weekly_rating_change": weekly_change,
                "top_negative_topic": top_neg,
            })
        return results

    def get_topic_distributions(self, property_id: int | None = None) -> list[dict]:
        """Calculates positive and negative mention counts across the 8 standard operational topics."""
        topics = list(classifier.TOPIC_KEYWORDS.keys())

        # Denominators: count total reviews, negative reviews, positive reviews
        q = self.db.query(Review)
        if property_id:
            q = q.filter(Review.property_id == property_id)
        reviews = q.all()

        total_neg_reviews = sum(1 for r in reviews if r.rating <= 5.5)
        total_pos_reviews = sum(1 for r in reviews if r.rating >= 7.0)

        results = []
        for topic in topics:
            tq = (
                self.db.query(ReviewTopic.sentiment, func.count(ReviewTopic.id))
                .join(Review, Review.id == ReviewTopic.review_id)
                .filter(ReviewTopic.topic == topic)
            )
            if property_id:
                tq = tq.filter(Review.property_id == property_id)

            counts = dict(tq.group_by(ReviewTopic.sentiment).all())
            pos_cnt = counts.get("Positive", 0)
            neg_cnt = counts.get("Negative", 0) + counts.get("Mixed", 0)
            total_mentions = pos_cnt + neg_cnt + counts.get("Neutral", 0)

            neg_pct = (
                round((neg_cnt / total_neg_reviews) * 100, 1)
                if total_neg_reviews > 0
                else 0.0
            )
            pos_pct = (
                round((pos_cnt / total_pos_reviews) * 100, 1)
                if total_pos_reviews > 0
                else 0.0
            )

            results.append({
                "topic": topic,
                "positive_count": pos_cnt,
                "negative_count": neg_cnt,
                "total_mentions": total_mentions,
                "negative_percentage_of_negative_reviews": neg_pct,
                "positive_percentage_of_positive_reviews": pos_pct,
            })

        # Sort by negative count descending
        results.sort(key=lambda x: x["negative_count"], reverse=True)
        return results

    def get_operational_insights(self, property_id: int | None = None) -> list[dict]:
        """Generates dynamic operational insights comparing current period vs previous period."""
        curr_start, curr_end, prev_start, prev_end = self._get_weekly_ranges()

        # Query reviews
        q = self.db.query(Review)
        if property_id:
            q = q.filter(Review.property_id == property_id)
        all_reviews = q.all()

        curr_reviews = [r for r in all_reviews if curr_start <= r.review_date <= curr_end]
        prev_reviews = [r for r in all_reviews if prev_start <= r.review_date <= prev_end]

        curr_neg = [r for r in curr_reviews if r.rating <= 6.0]
        prev_neg = [r for r in prev_reviews if r.rating <= 6.0]

        curr_neg_count = len(curr_neg)
        prev_neg_count = len(prev_neg)

        insights = []
        topics = list(classifier.TOPIC_KEYWORDS.keys())

        for topic in topics:
            # Query negative mentions for topic in current period
            curr_topic_reviews = (
                self.db.query(Review)
                .join(ReviewTopic, ReviewTopic.review_id == Review.id)
                .filter(
                    ReviewTopic.topic == topic,
                    ReviewTopic.sentiment.in_(["Negative", "Mixed"]),
                    Review.review_date.between(curr_start, curr_end),
                )
            )
            if property_id:
                curr_topic_reviews = curr_topic_reviews.filter(Review.property_id == property_id)
            curr_matches = curr_topic_reviews.all()
            curr_topic_count = len(curr_matches)

            # Query negative mentions in previous period
            prev_topic_reviews = (
                self.db.query(Review)
                .join(ReviewTopic, ReviewTopic.review_id == Review.id)
                .filter(
                    ReviewTopic.topic == topic,
                    ReviewTopic.sentiment.in_(["Negative", "Mixed"]),
                    Review.review_date.between(prev_start, prev_end),
                )
            )
            if property_id:
                prev_topic_reviews = prev_topic_reviews.filter(Review.property_id == property_id)
            prev_matches = prev_topic_reviews.all()
            prev_topic_count = len(prev_matches)

            curr_pct = round((curr_topic_count / curr_neg_count) * 100, 1) if curr_neg_count > 0 else 0.0
            prev_pct = round((prev_topic_count / prev_neg_count) * 100, 1) if prev_neg_count > 0 else 0.0
            pct_change = round(curr_pct - prev_pct, 1)

            # Find affected properties
            affected_prop_ids = list(set(r.property_id for r in curr_matches))
            affected_props = [
                p.name for p in self.db.query(Property).filter(Property.id.in_(affected_prop_ids)).all()
            ]

            # Collect supporting sample reviews
            supporting_samples = []
            for r in curr_matches[:3]:
                supporting_samples.append({
                    "id": r.id,
                    "property_name": r.property.name if r.property else "Unknown",
                    "rating": r.rating,
                    "review_date": r.review_date.isoformat(),
                    "title": r.title,
                    "negative_text": r.negative_text,
                    "positive_text": r.positive_text,
                })

            if curr_topic_count > 0 or prev_topic_count > 0:
                if pct_change > 0:
                    category = "warning"
                    trend = "worsening"
                    headline = f"{topic} mentioned in {curr_pct}% of negative reviews this week, up from {prev_pct}% last week (+{pct_change}%)."
                    interpretation = (
                        f"Operational alert: guest dissatisfaction regarding {topic.lower()} has escalated. "
                        f"Immediate maintenance or operational review is recommended across {', '.join(affected_props) or 'affected hotels'}."
                    )
                elif pct_change < 0:
                    category = "positive"
                    trend = "improving"
                    headline = f"{topic} concerns dropped to {curr_pct}% of negative reviews this week compared to {prev_pct}% last week ({pct_change}%)."
                    interpretation = (
                        f"Positive progress: operational remedies regarding {topic.lower()} are showing measurable improvement."
                    )
                else:
                    category = "neutral"
                    trend = "stable"
                    headline = f"{topic} remained steady at {curr_pct}% of negative reviews this week."
                    interpretation = f"{topic} complaints remain consistent with previous week baseline."

                insights.append({
                    "headline": headline,
                    "topic": topic,
                    "category": category,
                    "negative_reviews_percentage_current": curr_pct,
                    "negative_reviews_percentage_previous": prev_pct,
                    "percentage_change": pct_change,
                    "affected_properties": affected_props,
                    "supporting_reviews": supporting_samples,
                    "interpretation": interpretation,
                })

        # Sort insights by percentage change descending so critical warnings appear first
        insights.sort(key=lambda x: (x["category"] == "warning", abs(x["percentage_change"])), reverse=True)
        return insights

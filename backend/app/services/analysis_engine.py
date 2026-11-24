"""Review Analysis Engine.

Implements sentiment classification and operational topic classification for hotel guest reviews.
Designed with a pluggable BaseClassifier architecture so an LLM or ML classifier
can be swapped in seamlessly.
"""

from abc import ABC, abstractmethod
import re
from typing import TypedDict


class TopicClassificationResult(TypedDict):
    topic: str
    sentiment: str  # Positive, Negative, Mixed, Neutral
    confidence: float
    matched_keywords: list[str]


class AnalysisResult(TypedDict):
    overall_sentiment: str  # Positive, Negative, Mixed, Neutral
    topics: list[TopicClassificationResult]


class BaseClassifier(ABC):
    @abstractmethod
    def analyze(
        self,
        title: str | None,
        positive_text: str | None,
        negative_text: str | None,
        rating: float,
    ) -> AnalysisResult:
        pass


class KeywordRuleClassifier(BaseClassifier):
    """Keyword and rule-based classifier with word-boundary matching and negation handling."""

    # 8 Standard Operational Topics with domain keywords
    TOPIC_KEYWORDS = {
        "Cleanliness": [
            "dirty", "clean", "dusty", "dust", "stain", "stains", "stained",
            "unhygienic", "housekeeping", "hygiene", "tidy", "filthy", "smell",
            "odour", "odor", "linen", "sheet", "sheets", "bedsheet", "towel",
            "towels", "mold", "mould", "cockroach", "bugs", "bug", "gross"
        ],
        "Check-in experience": [
            "check-in", "check in", "checkin", "check-out", "check out", "checkout",
            "reception", "waiting", "wait", "keys", "key", "keycard", "booking process",
            "queue", "front desk", "arrival", "early check-in", "late check-in", "registration"
        ],
        "Staff and receptionist behaviour": [
            "staff", "receptionist", "friendly", "rude", "helpful", "unprofessional",
            "polite", "welcoming", "attitude", "host", "manager", "courteous",
            "attentive", "unfriendly", "incompetent", "hospitality", "customer service"
        ],
        "Noise": [
            "noisy", "noise", "loud", "traffic", "disturbance", "soundproof",
            "soundproofing", "quiet", "street noise", "neighbour", "neighbours",
            "neighbor", "neighbors", "footsteps", "thin walls", "siren", "sirens",
            "drilling", "screaming", "party", "banging", "earplugs"
        ],
        "Facilities": [
            "wifi", "wi-fi", "internet", "elevator", "lift", "air conditioning",
            "ac", "a/c", "amenities", "facility", "facilities", "gym", "pool",
            "swimming pool", "kettle", "television", "tv", "iron", "heater",
            "heating", "fridge", "refrigerator", "microwave", "hairdryer"
        ],
        "Location": [
            "location", "nearby", "convenient", "transport", "station", "distance",
            "central", "walk", "walking distance", "bus", "train", "metro",
            "harbour", "harbor", "cbd", "surry hills", "paddington", "potts point",
            "darling harbour", "shops", "restaurants", "close to"
        ],
        "Room condition": [
            "room", "broken", "damaged", "maintenance", "furniture", "bathroom",
            "bed", "mattress", "shower", "water pressure", "leak", "leaks",
            "cramped", "small room", "tiny", "spacious", "modern", "outdated",
            "old", "tired", "rundown", "toilet", "plumbing", "hot water", "lighting"
        ],
        "Value for money": [
            "value", "price", "expensive", "overpriced", "affordable", "worth",
            "money", "cost", "costly", "rip off", "ripoff", "bargain", "cheap",
            "rate", "rates", "economical", "overcharged", "overcharge"
        ],
    }

    # Polarity keywords for text analysis
    POSITIVE_WORDS = {
        "great", "good", "excellent", "clean", "friendly", "helpful", "convenient",
        "comfortable", "amazing", "wonderful", "perfect", "lovely", "spacious",
        "quiet", "recommend", "best", "loved", "enjoyed", "fast", "easy", "worth",
        "satisfied", "pleasant", "nice", "modern", "fantastic", "superb"
    }

    NEGATIVE_WORDS = {
        "bad", "terrible", "horrible", "dirty", "rude", "unhelpful", "noisy",
        "uncomfortable", "broken", "worst", "awful", "disappointing", "poor",
        "slow", "smelly", "stained", "cramped", "overpriced", "loud", "frustrating",
        "disgusting", "unacceptable", "nightmare", "useless", "dated", "cold"
    }

    NEGATION_WORDS = {"not", "never", "no", "wasn't", "weren't", "didn't", "hardly", "barely", "scarcely", "cannot", "can't"}

    def _clean_text(self, text: str | None) -> str:
        if not text:
            return ""
        # Filter out common filler strings
        cleaned = text.strip()
        if cleaned.lower() in {"none", "n/a", "na", "nil", "nothing", "-", "no", "no negative", "no positive"}:
            return ""
        return cleaned

    def _has_negation_before(self, words: list[str], idx: int, window: int = 3) -> bool:
        start = max(0, idx - window)
        for i in range(start, idx):
            if words[i].lower() in self.NEGATION_WORDS:
                return True
        return False

    def _extract_matches_for_topic(self, text: str, keywords: list[str]) -> list[str]:
        if not text:
            return []
        matched = []
        lower_text = text.lower()
        for kw in keywords:
            # Word boundary regex matching
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, lower_text):
                matched.append(kw)
        return matched

    def _classify_topic_sentiment(
        self,
        topic: str,
        matched_in_pos: list[str],
        matched_in_neg: list[str],
        matched_in_title: list[str],
        overall_rating: float,
    ) -> str:
        if matched_in_pos and not matched_in_neg:
            return "Positive"
        if matched_in_neg and not matched_in_pos:
            return "Negative"
        if matched_in_pos and matched_in_neg:
            return "Mixed"
        # If mentioned only in title or general text, fall back to rating polarity
        if matched_in_title:
            if overall_rating >= 7.5:
                return "Positive"
            if overall_rating <= 5.5:
                return "Negative"
            return "Neutral"
        return "Neutral"

    def analyze(
        self,
        title: str | None,
        positive_text: str | None,
        negative_text: str | None,
        rating: float,
    ) -> AnalysisResult:
        c_title = self._clean_text(title)
        c_pos = self._clean_text(positive_text)
        c_neg = self._clean_text(negative_text)

        # 1. Determine Overall Review Sentiment
        # Considers rating AND positive/negative text presence & polarity
        has_pos = len(c_pos) > 10
        has_neg = len(c_neg) > 10

        if has_pos and not has_neg:
            if rating >= 6.5:
                overall_sentiment = "Positive"
            elif rating <= 4.0:
                overall_sentiment = "Mixed"  # written positive text but low score
            else:
                overall_sentiment = "Neutral"
        elif has_neg and not has_pos:
            if rating <= 6.0:
                overall_sentiment = "Negative"
            elif rating >= 8.0:
                overall_sentiment = "Mixed"  # written negative text but high score
            else:
                overall_sentiment = "Negative"
        elif has_pos and has_neg:
            if rating >= 8.5 and len(c_pos) > 2 * len(c_neg):
                overall_sentiment = "Positive"
            elif rating <= 4.5 and len(c_neg) > 2 * len(c_pos):
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Mixed"
        else:
            # Neither detailed pos nor neg text provided: rely primarily on numerical rating
            if rating >= 7.5:
                overall_sentiment = "Positive"
            elif rating <= 5.0:
                overall_sentiment = "Negative"
            elif 5.0 < rating < 7.0:
                overall_sentiment = "Neutral"
            else:
                overall_sentiment = "Neutral"

        # 2. Operational Topic Classification
        topics_result: list[TopicClassificationResult] = []

        for topic_name, keywords in self.TOPIC_KEYWORDS.items():
            pos_matches = self._extract_matches_for_topic(c_pos, keywords)
            neg_matches = self._extract_matches_for_topic(c_neg, keywords)
            title_matches = self._extract_matches_for_topic(c_title, keywords)

            all_matched = list(dict.fromkeys(pos_matches + neg_matches + title_matches))
            if all_matched:
                sentiment = self._classify_topic_sentiment(
                    topic_name, pos_matches, neg_matches, title_matches, rating
                )
                # Confidence score: base 0.8, up to 1.0 depending on number of matches
                conf = min(1.0, 0.75 + 0.1 * len(all_matched))
                topics_result.append({
                    "topic": topic_name,
                    "sentiment": sentiment,
                    "confidence": round(conf, 2),
                    "matched_keywords": all_matched,
                })

        return {
            "overall_sentiment": overall_sentiment,
            "topics": topics_result,
        }


# Singleton classifier instance (can be swapped for LLMClassifier)
classifier: BaseClassifier = KeywordRuleClassifier()

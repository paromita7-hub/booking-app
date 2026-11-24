from app.services.analysis_engine import classifier


def test_sentiment_classification_positive():
    """Verify strong positive review text and high score results in Positive sentiment."""
    result = classifier.analyze(
        title="Wonderful stay",
        positive_text="The room was spotless and clean, staff was super friendly.",
        negative_text="None",
        rating=9.0,
    )
    assert result["overall_sentiment"] == "Positive"
    topics = {t["topic"]: t["sentiment"] for t in result["topics"]}
    assert "Cleanliness" in topics
    assert topics["Cleanliness"] == "Positive"
    assert "Staff and receptionist behaviour" in topics
    assert topics["Staff and receptionist behaviour"] == "Positive"


def test_sentiment_classification_negative():
    """Verify severe complaints and low score results in Negative sentiment."""
    result = classifier.analyze(
        title="Terrible experience",
        positive_text=None,
        negative_text="The bathroom was dirty and unhygienic with visible mold. Receptionist was rude.",
        rating=3.0,
    )
    assert result["overall_sentiment"] == "Negative"
    topics = {t["topic"]: t["sentiment"] for t in result["topics"]}
    assert "Cleanliness" in topics
    assert topics["Cleanliness"] == "Negative"
    assert "Staff and receptionist behaviour" in topics
    assert topics["Staff and receptionist behaviour"] == "Negative"


def test_sentiment_classification_mixed():
    """Verify review with both substantial praise and complaints results in Mixed sentiment."""
    result = classifier.analyze(
        title="Good location but noisy",
        positive_text="The location near Central Station was unbeatable for getting around town.",
        negative_text="Street traffic was extremely loud and noisy all night with thin walls.",
        rating=6.5,
    )
    assert result["overall_sentiment"] == "Mixed"
    topics = {t["topic"]: t["sentiment"] for t in result["topics"]}
    assert "Location" in topics
    assert topics["Location"] == "Positive"
    assert "Noise" in topics
    assert topics["Noise"] == "Negative"


def test_all_eight_operational_topics_detection():
    """Verify all 8 topics are correctly detected."""
    test_cases = [
        ("Cleanliness", "The sheets and towels were dirty and stained.", 4.0),
        ("Check-in experience", "Waited 40 minutes at reception during check-in.", 4.0),
        ("Staff and receptionist behaviour", "The receptionist was very friendly and helpful.", 8.5),
        ("Noise", "Constant traffic disturbance and thin walls.", 4.0),
        ("Facilities", "The elevator was broken and wifi was offline.", 3.5),
        ("Location", "Great location within walking distance of the station.", 9.0),
        ("Room condition", "Damaged furniture and low water pressure in the shower.", 4.5),
        ("Value for money", "Far too expensive and not worth the overpriced rate.", 4.0),
    ]

    for topic_name, text, rating in test_cases:
        res = classifier.analyze(title=topic_name, positive_text=text, negative_text=text, rating=rating)
        detected_topics = [t["topic"] for t in res["topics"]]
        assert topic_name in detected_topics, f"Failed to detect {topic_name} in text: '{text}'"

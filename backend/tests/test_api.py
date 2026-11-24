import io


def test_properties_api(client):
    res = client.get("/api/properties")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4
    prop_names = [p["name"] for p in data]
    assert "Olympic Hotel Paddington" in prop_names
    assert "Darling Harbour" in prop_names


def test_reviews_pagination_and_filtering(client):
    # Import a review via API
    csv_content = """property_id,rating,review_date,title,positive_text,negative_text
1,9.0,2026-11-20,Excellent,Very clean,None
"""
    upload_res = client.post(
        "/api/reviews/import",
        files={"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )
    assert upload_res.status_code == 200
    assert upload_res.json()["records_added"] == 1

    # Query reviews
    res = client.get("/api/reviews?page=1&limit=10")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["rating"] == 9.0


def test_csv_template_download(client):
    res = client.get("/api/reviews/template")
    assert res.status_code == 200
    assert "property_name" in res.text
    assert "rating" in res.text


def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert "sydney_time" in data

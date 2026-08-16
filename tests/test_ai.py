def test_api_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_ai_analysis_endpoint(client):
    response = client.post(
        "/api/v1/analyze",
        headers={"X-API-Key": "test-key"},
        json={
            "subject": "Unauthorised card transaction",
            "message": "There is an unauthorised credit card transaction on my account and I need urgent help.",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "category" in data
    assert "sentiment" in data
    assert "retrieval" in data
    assert data["human_approval_required"] is True

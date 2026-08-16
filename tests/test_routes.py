def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Customer Support" in response.data


def test_register_and_dashboard(client):
    response = client.post(
        "/auth/register",
        data={"username": "demo_user", "password": "StrongPass123!", "confirm": "StrongPass123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Complaint dashboard" in response.data

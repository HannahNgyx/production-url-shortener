from fastapi.testclient import TestClient
from app.main import app

def test_shorten_url():
    with TestClient(app) as client:
        response = client.post("/urls", params={"url": "https://www.google.com"})
        assert response.status_code == 200
        assert response.json()["original_url"] == "https://www.google.com"
        assert response.json()["short_url"].startswith("http://localhost:8000/")
        assert len(response.json()["code"]) == 6

def test_get_url():
    with TestClient(app) as client:
        response = client.post("/urls", params={"url": "https://www.google.com"})
        response = client.get(f"/{response.json()['code']}", follow_redirects=False)
        assert response.status_code == 302 
        assert response.headers["location"] == "https://www.google.com"

def test_get_url_not_found():
    with TestClient(app) as client:
        response = client.get("/123456", follow_redirects=False)
        assert response.status_code == 404
        assert response.json() == {"detail": "Unknown code"}
        
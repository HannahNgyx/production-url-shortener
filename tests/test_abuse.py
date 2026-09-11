from fastapi.testclient import TestClient
from app.main import app

def test_invalid_url():
    with TestClient(app) as client:
        response = client.post("/urls", params={"url": "javascript:alert(1)"})
        assert response.status_code == 422
        assert response.json() == {"detail": "Invalid URL"}

def test_huge_url():
    with TestClient(app) as client:
        response = client.post("/urls", params={"url": "https://example.com" + "a"*2048})
        assert response.status_code == 422
        assert response.json() == {"detail": "This URL is too long"}

def test_missing_host():
    with TestClient(app) as client:
        response = client.post("/urls", params={"url": "https://"})
        assert response.status_code == 422
        assert response.json() == {"detail": "Invalid URL"}

def test_empty_url():
    with TestClient(app) as client:
        response = client.post("/urls", params={"url": " "})
        assert response.status_code == 422
        assert response.json() == {"detail": "Empty URL"}

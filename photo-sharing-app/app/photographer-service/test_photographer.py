import json
import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from photographer_service import app

headers_content = {"Content-Type": "application/json"}

data1 = {
    "display_name": "rdoisneau",
    "first_name": "robert",
    "last_name": "doisneau",
    "interests": ["street", "portrait"],
}

data2 = {
    "display_name": "adams",
    "first_name": "ansel",
    "last_name": "adams",
    "interests": ["landscape", "black_and_white"],
}

@pytest.mark.asyncio
@pytest.mark.usefixtures("clearPhotographers")
@pytest.mark.usefixtures("initDB")
async def test_post_once():
    """Test de création d'un photographe."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as ac:
        response = await ac.post(
            "/photographers", headers=headers_content, content=json.dumps(data1)
        )
        assert response.status_code == 201, f"Code de réponse inattendu : {response.status_code}"
        response_data = response.json()
        assert response_data is not None, "La réponse ne contient pas de données JSON."
        assert response_data["display_name"] == data1["display_name"], "Display name incorrect."
        assert response_data["first_name"] == data1["first_name"], "First name incorrect."
        assert response_data["last_name"] == data1["last_name"], "Last name incorrect."
        assert response_data["interests"] == data1["interests"], "Interests incorrects."


@pytest.mark.asyncio
@pytest.mark.usefixtures("clearPhotographers")
@pytest.mark.usefixtures("initDB")
async def test_post_twice():
    """Test d'ajout de deux photographes et détection des doublons."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as ac:
        response1 = await ac.post(
            "/photographers", headers=headers_content, content=json.dumps(data1)
        )
        assert response1.status_code == 201, f"Code de réponse inattendu : {response1.status_code}"

        response2 = await ac.post(
            "/photographers", headers=headers_content, content=json.dumps(data1)
        )
        assert response2.status_code == 409, f"Code de réponse inattendu : {response2.status_code}"

@pytest.mark.asyncio
@pytest.mark.usefixtures("clearPhotographers")
@pytest.mark.usefixtures("initDB")
async def test_has_more_false_photographers():
    """Test de pagination avec moins de photographes que la limite."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as ac:
        response = await ac.post(
            "/photographers", headers=headers_content, content=json.dumps(data1)
        )
        assert response.status_code == 201

        response = await ac.get("/photographers?limit=10")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["has_more"] is False

@pytest.mark.asyncio
@pytest.mark.usefixtures("clearPhotographers")
@pytest.mark.usefixtures("initDB")
async def test_has_more_true_photographers():
    """Test de pagination avec plus de photographes que la limite."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as ac:
        await ac.post(
            "/photographers", headers=headers_content, content=json.dumps(data1)
        )
        await ac.post(
            "/photographers", headers=headers_content, content=json.dumps(data2)
        )

        response = await ac.get("/photographers?limit=1")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["has_more"] is True

@pytest.mark.asyncio
@pytest.mark.usefixtures("clearPhotographers")
@pytest.mark.usefixtures("initDB")
async def test_delete_photographer():
    """Test de suppression d'un photographe."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as ac:
        response = await ac.post(
            "/photographers", headers=headers_content, content=json.dumps(data1)
        )
        assert response.status_code == 201

        response = await ac.delete(f"/photographer/{data1['display_name']}")
        assert response.status_code == 204

        response = await ac.get(f"/photographer/{data1['display_name']}")
        assert response.status_code == 404

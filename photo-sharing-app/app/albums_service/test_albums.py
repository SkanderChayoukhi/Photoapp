import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from albums_service import app
# from conftest import initDB, clearAlbums, sample_album


client = TestClient(app)

@patch("requests.get")
def test_create_album(mock_get, initDB, clearAlbums):
    """Test creating an album with a mocked photographer-service response."""
    mock_get.return_value.status_code = 200  # Mock photographer exists
    
    response = client.post("/photographers/test_photographer/albums", json={
        "title": "My Album",
        "description": "Test Description",
        "cover_photo_id": "photo123"
    })
    
    assert response.status_code == 201
    assert response.json()["title"] == "My Album"
    assert response.json()["description"] == "Test Description"
    assert response.json()["cover_photo_id"] == "photo123"

@patch("requests.get")
def test_create_album_photographer_not_found(mock_get, initDB, clearAlbums):
    """Test creating an album when photographer does not exist."""
    mock_get.return_value.status_code = 404  # Mock photographer not found
    
    response = client.post("/photographers/nonexistent/albums", json={
        "title": "Test Album",
        "description": "Sample description",
        "cover_photo_id": "photo123"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Photographer Not Found"

@patch("requests.get")
def test_create_album_photographer_service_unavailable(mock_get, initDB, clearAlbums):
    """Test creating an album when photographer-service is unavailable."""
    mock_get.return_value.status_code = 503  # Mock service unavailable
    
    response = client.post("/photographers/test_photographer/albums", json={
        "title": "Album",
        "description": "Test desc",
        "cover_photo_id": "photo123"
    })
    
    assert response.status_code == 503
    assert response.json()["detail"] == "Photographer Service Unavailable"


@patch("requests.get")
def test_retrieve_all_albums(mock_get, initDB, clearAlbums, sample_album):
    """Test retrieving all albums for a photographer."""
    mock_get.return_value.status_code = 200  # Mock photographer exists
    
    response = client.get("/photographers/test_photographer/albums")
    
    assert response.status_code == 200
    assert len(response.json()["items"]) > 0
    assert response.json()["items"][0]["title"] == "Test Album"

    
@patch("requests.get")
def test_retrieve_specific_album(mock_get, initDB, clearAlbums, sample_album):
    """Test retrieving a specific album by ID."""
    mock_get.return_value.status_code = 200  # Mock photographer exists
    
    response = client.get(f"/photographers/test_photographer/albums/{sample_album.album_id}")
    
    assert response.status_code == 200
    assert response.json()["title"] == "Test Album"
    assert response.json()["description"] == "A sample test album"    


@patch("requests.get")
def test_update_album(mock_get, initDB, clearAlbums, sample_album):
    """Test updating an album."""
    mock_get.return_value.status_code = 200  # Mock photographer exists
    
    response = client.put(f"/photographers/test_photographer/albums/{sample_album.album_id}", json={
        "title": "Updated Album Title",
        "description": "Updated description",
        "cover_photo_id": "updated_photo123"
    })
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Album Title"
    assert response.json()["description"] == "Updated description"
    assert response.json()["cover_photo_id"] == "updated_photo123"


@patch("requests.get")
def test_delete_album(mock_get, initDB, clearAlbums, sample_album):
    """Test deleting an album."""
    mock_get.return_value.status_code = 200  # Mock photographer exists
    
    response = client.delete(f"/photographers/test_photographer/albums/{sample_album.album_id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Album successfully deleted"


@patch("requests.get")
@patch("requests.get")  # Mock photo-service separately

def test_add_photo_to_album(mock_get_photographer, mock_get_photo, initDB, clearAlbums, sample_album):
    """Test adding a photo to an album with mocked photographer-service and photo-service responses."""
    mock_get_photographer.return_value.status_code = 200  # Mock photographer exists
    mock_get_photo.return_value.status_code = 200  # Mock photo exists in photo-service
    
    response = client.post(f"/photographers/test_photographer/albums/{sample_album.album_id}/photos", json={
        "photo_id": "photo123"
    })
    
    assert response.status_code == 201
    assert "photo123" in response.json()["photos"]



@patch("requests.get")
@patch("requests.get")  # Mock photo-service separately
def test_remove_photo_from_album(mock_get_photographer, mock_get_photo, initDB, clearAlbums, sample_album):
    """Test removing a photo from an album with mocked photographer-service and photo-service responses."""
    mock_get_photographer.return_value.status_code = 200  # Mock photographer exists
    mock_get_photo.return_value.status_code = 200  # Mock photo exists in photo-service
    
    response = client.delete(f"/photographers/test_photographer/albums/{sample_album.album_id}/photos/photo123")
    
    assert response.status_code == 200
    assert "photo123" not in response.json()["photos"]


@patch("requests.get")
@patch("requests.get")  # Mock photo-service separately
def test_retrieve_photos_in_album(mock_get_photographer, mock_get_photo, initDB, clearAlbums, sample_album):
    """Test retrieving photos in an album with mocked photographer-service and photo-service responses."""
    mock_get_photographer.return_value.status_code = 200  # Mock photographer exists
    mock_get_photo.return_value.status_code = 200  # Mock photo metadata retrieval from photo-service
    mock_get_photo.return_value.json.return_value = {
        "photo_id": "photo123",
        "title": "Sample Photo",
        "location": "Test Location",
        "tags": ["landscape", "nature"]
    }
    
    response = client.get(f"/photographers/test_photographer/albums/{sample_album.album_id}/photos")
    
    assert response.status_code == 200
    assert len(response.json()["photos"]) > 0
    assert response.json()["photos"][0]["photo_id"] == "photo123"
    assert response.json()["photos"][0]["title"] == "Sample Photo"








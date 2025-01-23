import pytest
from mongoengine import connect, disconnect
from models import Album

@pytest.fixture(scope="class")
def initDB():
    """Establishes a test database connection for albums service."""
    disconnect()  # Ensure no previous connections exist
    connect("test_albums_db", alias="default", host="mongo-service-test")
    yield
    disconnect()  # Cleanup after tests

@pytest.fixture()
def clearAlbums():
    """Clears all album entries before each test."""
    Album.objects.all().delete()

@pytest.fixture()
def sample_album():
    """Creates a sample album for testing."""
    album = Album(
        display_name="test_photographer",
        album_id="album123",
        title="Test Album",
        description="A sample test album",
        cover_photo_id="photo1",
        photos=["photo1", "photo2","photo123"]
    )
    album.save()
    yield album
    album.delete()  # Cleanup after test execution

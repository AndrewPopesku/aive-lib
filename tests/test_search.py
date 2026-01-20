"""Tests for SearchService."""

import hashlib
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from aive.services.search import SearchService
from aive.models import SearchResult
from aive.errors import SearchConfigError, SearchError


# Sample API responses
PEXELS_VIDEO_RESPONSE = {
    "videos": [
        {
            "id": 27095078,
            "width": 3840,
            "height": 2160,
            "duration": 5,
            "url": "https://www.pexels.com/video/nature-sunset-27095078/",
            "image": "https://images.pexels.com/videos/27095078/preview.jpeg",
            "user": {"name": "John Doe"},
            "video_files": [
                {
                    "id": 12070224,
                    "quality": "hd",
                    "file_type": "video/mp4",
                    "width": 1920,
                    "height": 1080,
                    "link": "https://videos.pexels.com/video-files/27095078/1920_1080_30fps.mp4",
                }
            ],
        }
    ]
}

PEXELS_PHOTO_RESPONSE = {
    "photos": [
        {
            "id": 20727530,
            "width": 4000,
            "height": 6000,
            "photographer": "Alex Ravvas",
            "alt": "Beautiful sunset over ocean",
            "src": {
                "original": "https://images.pexels.com/photos/20727530/pexels-photo.jpeg",
                "medium": "https://images.pexels.com/photos/20727530/medium.jpg",
            },
        }
    ]
}

PIXABAY_VIDEO_RESPONSE = {
    "total": 100,
    "totalHits": 50,
    "hits": [
        {
            "id": 111204,
            "duration": 16,
            "tags": "sunset, nature, sky",
            "user": "PixabayUser",
            "videos": {
                "large": {
                    "url": "https://cdn.pixabay.com/video/111204/large.mp4",
                    "width": 1920,
                    "height": 1080,
                    "thumbnail": "https://cdn.pixabay.com/video/111204/large.jpg",
                }
            },
        }
    ],
}

PIXABAY_IMAGE_RESPONSE = {
    "hits": [
        {
            "id": 7373484,
            "tags": "landscape, rainbow, tropical",
            "previewURL": "https://cdn.pixabay.com/photo/7373484/150.jpg",
            "largeImageURL": "https://pixabay.com/get/7373484_1280.jpg",
            "imageWidth": 3150,
            "imageHeight": 2100,
            "user": "Kanenori",
        }
    ]
}

JAMENDO_RESPONSE = {
    "headers": {"status": "success", "code": 0, "results_count": 1},
    "results": [
        {
            "id": "1446611",
            "name": "Great and beautiful view",
            "duration": 245,
            "artist_name": "Giocol",
            "audio": "https://prod-1.storage.jamendo.com/?trackid=1446611&format=mp31",
            "audiodownload": "https://prod-1.storage.jamendo.com/download/track/1446611/mp32/",
        }
    ],
}


@pytest.fixture
def search_service(tmp_path):
    """Create a SearchService with a temporary cache directory."""
    return SearchService(cache_dir=tmp_path)


@pytest.fixture
def mock_env():
    """Mock environment variables for API keys."""
    with patch.dict(
        "os.environ",
        {
            "PEXELS_API_KEY": "test-pexels-key",
            "PIXABAY_API_KEY": "test-pixabay-key",
            "JAMENDO_CLIENT_ID": "test-jamendo-id",
        },
    ):
        yield


class TestSearchServiceConfig:
    """Tests for API key configuration."""

    def test_missing_pexels_key(self, search_service):
        """Test that missing Pexels key raises SearchConfigError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(SearchConfigError, match="PEXELS_API_KEY"):
                search_service._get_pexels_key()

    def test_missing_pixabay_key(self, search_service):
        """Test that missing Pixabay key raises SearchConfigError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(SearchConfigError, match="PIXABAY_API_KEY"):
                search_service._get_pixabay_key()

    def test_missing_jamendo_key(self, search_service):
        """Test that missing Jamendo client ID raises SearchConfigError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(SearchConfigError, match="JAMENDO_CLIENT_ID"):
                search_service._get_jamendo_client_id()

    def test_get_pexels_key(self, search_service, mock_env):
        """Test getting Pexels API key."""
        assert search_service._get_pexels_key() == "test-pexels-key"

    def test_get_pixabay_key(self, search_service, mock_env):
        """Test getting Pixabay API key."""
        assert search_service._get_pixabay_key() == "test-pixabay-key"

    def test_get_jamendo_client_id(self, search_service, mock_env):
        """Test getting Jamendo client ID."""
        assert search_service._get_jamendo_client_id() == "test-jamendo-id"


class TestPexelsSearch:
    """Tests for Pexels API integration."""

    @pytest.mark.asyncio
    async def test_search_pexels_videos(self, search_service, mock_env):
        """Test searching Pexels for videos."""
        mock_response = MagicMock()
        mock_response.json.return_value = PEXELS_VIDEO_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            results = await search_service.search_media(
                "sunset", "pexels", "video", limit=5
            )

            assert len(results) == 1
            assert results[0].id == "27095078"
            assert results[0].provider == "pexels"
            assert results[0].media_type == "video"
            assert results[0].duration == 5
            assert results[0].author == "John Doe"

    @pytest.mark.asyncio
    async def test_search_pexels_photos(self, search_service, mock_env):
        """Test searching Pexels for photos."""
        mock_response = MagicMock()
        mock_response.json.return_value = PEXELS_PHOTO_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            results = await search_service.search_media(
                "sunset", "pexels", "image", limit=5
            )

            assert len(results) == 1
            assert results[0].id == "20727530"
            assert results[0].provider == "pexels"
            assert results[0].media_type == "image"
            assert results[0].width == 4000
            assert results[0].height == 6000
            assert results[0].author == "Alex Ravvas"


class TestPixabaySearch:
    """Tests for Pixabay API integration."""

    @pytest.mark.asyncio
    async def test_search_pixabay_videos(self, search_service, mock_env):
        """Test searching Pixabay for videos."""
        mock_response = MagicMock()
        mock_response.json.return_value = PIXABAY_VIDEO_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            results = await search_service.search_media(
                "sunset", "pixabay", "video", limit=5
            )

            assert len(results) == 1
            assert results[0].id == "111204"
            assert results[0].provider == "pixabay"
            assert results[0].media_type == "video"
            assert results[0].duration == 16
            assert results[0].author == "PixabayUser"

    @pytest.mark.asyncio
    async def test_search_pixabay_images(self, search_service, mock_env):
        """Test searching Pixabay for images."""
        mock_response = MagicMock()
        mock_response.json.return_value = PIXABAY_IMAGE_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            results = await search_service.search_media(
                "landscape", "pixabay", "image", limit=5
            )

            assert len(results) == 1
            assert results[0].id == "7373484"
            assert results[0].provider == "pixabay"
            assert results[0].media_type == "image"
            assert results[0].width == 3150
            assert results[0].height == 2100


class TestJamendoSearch:
    """Tests for Jamendo API integration."""

    @pytest.mark.asyncio
    async def test_search_jamendo_music(self, search_service, mock_env):
        """Test searching Jamendo for music."""
        mock_response = MagicMock()
        mock_response.json.return_value = JAMENDO_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            results = await search_service.search_music("relaxing", limit=5)

            assert len(results) == 1
            assert results[0].id == "1446611"
            assert results[0].provider == "jamendo"
            assert results[0].media_type == "audio"
            assert results[0].duration == 245
            assert results[0].title == "Great and beautiful view"
            assert results[0].author == "Giocol"


class TestDownload:
    """Tests for media download functionality."""

    @pytest.mark.asyncio
    async def test_download_video(self, search_service, mock_env):
        """Test downloading a video file."""
        result = SearchResult(
            id="12345",
            url="https://example.com/video.mp4",
            provider="pexels",
            media_type="video",
        )

        mock_response = MagicMock()
        mock_response.content = b"fake video content"
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            path = await search_service.download(result)

            # Filename is now SHA-256 hash of "provider:id"
            expected_hash = hashlib.sha256("pexels:12345".encode()).hexdigest()
            assert path.exists()
            assert path.name == f"{expected_hash}.mp4"
            assert path.read_bytes() == b"fake video content"

    @pytest.mark.asyncio
    async def test_download_cached(self, search_service, mock_env):
        """Test that cached files are returned without re-downloading."""
        result = SearchResult(
            id="cached123",
            url="https://example.com/video.mp4",
            provider="pexels",
            media_type="video",
        )

        # Create cached file with hash-based filename
        cache_hash = hashlib.sha256("pexels:cached123".encode()).hexdigest()
        cache_path = search_service.cache_dir / f"{cache_hash}.mp4"
        cache_path.write_bytes(b"cached content")

        # Should return cached file without making HTTP request
        path = await search_service.download(result)

        assert path == cache_path
        assert path.read_bytes() == b"cached content"


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_unknown_provider_error(self, search_service, mock_env):
        """Test that unknown provider raises SearchError."""
        with pytest.raises(SearchError, match="Unknown provider"):
            await search_service.search_media("query", "unknown", "video", 10)

    @pytest.mark.asyncio
    async def test_http_error_handling(self, search_service, mock_env):
        """Test that HTTP errors are wrapped in SearchError."""
        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=httpx.HTTPError("Connection failed")
            )
            mock_get_client.return_value = mock_client

            with pytest.raises(SearchError, match="Pexels API error"):
                await search_service.search_media("query", "pexels", "video", 10)


class TestHelperMethods:
    """Tests for helper methods."""

    def test_select_best_video_file_1080p(self, search_service):
        """Test that 1080p is preferred when available."""
        video_files = [
            {"height": 720, "link": "720p.mp4"},
            {"height": 1080, "link": "1080p.mp4"},
            {"height": 2160, "link": "4k.mp4"},
        ]
        result = search_service._select_best_video_file(video_files)
        assert result["height"] == 1080

    def test_select_best_video_file_fallback(self, search_service):
        """Test fallback to highest quality when 1080p unavailable."""
        video_files = [
            {"height": 720, "link": "720p.mp4"},
            {"height": 480, "link": "480p.mp4"},
        ]
        result = search_service._select_best_video_file(video_files)
        assert result["height"] == 720

    def test_select_best_video_file_empty(self, search_service):
        """Test handling of empty video files list."""
        result = search_service._select_best_video_file([])
        assert result is None

    def test_extract_pexels_title(self, search_service):
        """Test extracting title from Pexels URL."""
        url = "https://www.pexels.com/video/beautiful-sunset-over-ocean-27095078/"
        title = search_service._extract_pexels_title(url)
        assert title == "Beautiful Sunset Over Ocean"

    def test_extract_pexels_title_empty(self, search_service):
        """Test handling of empty URL."""
        assert search_service._extract_pexels_title("") is None
        assert search_service._extract_pexels_title(None) is None


class TestLimitHandling:
    """Tests for limit parameter handling."""

    @pytest.mark.asyncio
    async def test_limit_clamped_to_max(self, search_service, mock_env):
        """Test that limit is clamped to maximum of 50."""
        mock_response = MagicMock()
        mock_response.json.return_value = PEXELS_VIDEO_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await search_service.search_media("query", "pexels", "video", limit=100)

            # Check that per_page was clamped to 50
            call_kwargs = mock_client.get.call_args
            assert call_kwargs[1]["params"]["per_page"] == 50

    @pytest.mark.asyncio
    async def test_limit_clamped_to_min(self, search_service, mock_env):
        """Test that limit is clamped to minimum of 1."""
        mock_response = MagicMock()
        mock_response.json.return_value = PEXELS_VIDEO_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            search_service, "_get_client", new_callable=AsyncMock
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await search_service.search_media("query", "pexels", "video", limit=0)

            # Check that per_page was clamped to 1
            call_kwargs = mock_client.get.call_args
            assert call_kwargs[1]["params"]["per_page"] == 1

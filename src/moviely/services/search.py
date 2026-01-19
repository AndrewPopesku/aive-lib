"""Search service for media providers (Pexels, Pixabay, Jamendo)."""

import os
import re
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urlparse

import aiofiles
import httpx

from moviely.errors import SearchConfigError, SearchError
from moviely.models import SearchResult


class SearchService:
    """Async search service for stock media providers."""

    PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
    PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"
    PIXABAY_VIDEO_URL = "https://pixabay.com/api/videos/"
    PIXABAY_IMAGE_URL = "https://pixabay.com/api/"
    JAMENDO_URL = "https://api.jamendo.com/v3.0/tracks/"

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the search service.

        Args:
            cache_dir: Directory for caching downloaded files.
                      Defaults to ~/.moviely/cache
        """
        self.cache_dir = cache_dir or Path.home() / ".moviely" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _get_pexels_key(self) -> str:
        """Get Pexels API key from environment."""
        key = os.environ.get("PEXELS_API_KEY")
        if not key:
            raise SearchConfigError(
                "PEXELS_API_KEY environment variable is not set. "
                "Get your API key at https://www.pexels.com/api/"
            )
        return key

    def _get_pixabay_key(self) -> str:
        """Get Pixabay API key from environment."""
        key = os.environ.get("PIXABAY_API_KEY")
        if not key:
            raise SearchConfigError(
                "PIXABAY_API_KEY environment variable is not set. "
                "Get your API key at https://pixabay.com/api/docs/"
            )
        return key

    def _get_jamendo_client_id(self) -> str:
        """Get Jamendo client ID from environment."""
        client_id = os.environ.get("JAMENDO_CLIENT_ID")
        if not client_id:
            raise SearchConfigError(
                "JAMENDO_CLIENT_ID environment variable is not set. "
                "Get your client ID at https://developer.jamendo.com/"
            )
        return client_id

    async def search_media(
        self,
        query: str,
        provider: Literal["pexels", "pixabay"],
        media_type: Literal["video", "image"],
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search for videos or images from a provider.

        Args:
            query: Search query string
            provider: Media provider ("pexels" or "pixabay")
            media_type: Type of media ("video" or "image")
            limit: Maximum number of results (default 10, max 50)

        Returns:
            List of SearchResult objects
        """
        limit = min(max(limit, 1), 50)

        if provider == "pexels":
            return await self._search_pexels(query, media_type, limit)
        elif provider == "pixabay":
            return await self._search_pixabay(query, media_type, limit)
        else:
            raise SearchError(f"Unknown provider: {provider}")

    async def search_music(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search for music tracks from Jamendo.

        Args:
            query: Search query string
            limit: Maximum number of results (default 10, max 50)

        Returns:
            List of SearchResult objects
        """
        limit = min(max(limit, 1), 50)
        return await self._search_jamendo(query, limit)

    async def download(self, result: SearchResult) -> Path:
        """Download a search result to local cache.

        Args:
            result: SearchResult to download

        Returns:
            Path to the downloaded file
        """
        # Determine file extension from URL
        parsed = urlparse(result.url)
        path_ext = Path(parsed.path).suffix
        if not path_ext:
            # Default extensions by media type
            ext_map = {"video": ".mp4", "image": ".jpg", "audio": ".mp3"}
            path_ext = ext_map.get(result.media_type, ".bin")

        # Create cache filename
        filename = f"{result.provider}_{result.id}{path_ext}"
        cache_path = self.cache_dir / filename

        # Return cached file if exists
        if cache_path.exists():
            return cache_path

        # Download the file
        client = await self._get_client()
        try:
            response = await client.get(result.url, follow_redirects=True)
            response.raise_for_status()

            async with aiofiles.open(cache_path, "wb") as f:
                await f.write(response.content)

            return cache_path
        except httpx.HTTPError as e:
            raise SearchError(f"Failed to download media: {e}") from e

    async def _search_pexels(
        self, query: str, media_type: Literal["video", "image"], limit: int
    ) -> list[SearchResult]:
        """Search Pexels for videos or images."""
        api_key = self._get_pexels_key()
        client = await self._get_client()

        if media_type == "video":
            url = self.PEXELS_VIDEO_URL
            params = {"query": query, "per_page": limit}
        else:
            url = self.PEXELS_PHOTO_URL
            params = {"query": query, "per_page": limit}

        headers = {"Authorization": api_key}

        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise SearchError(f"Pexels API error: {e}") from e

        results = []
        if media_type == "video":
            for video in data.get("videos", []):
                # Find best quality video file (prefer 1080p)
                video_files = video.get("video_files", [])
                best_file = self._select_best_video_file(video_files)
                if not best_file:
                    continue

                # Extract title from URL slug
                title = self._extract_pexels_title(video.get("url", ""))

                results.append(
                    SearchResult(
                        id=str(video["id"]),
                        url=best_file["link"],
                        preview_url=video.get("image"),
                        provider="pexels",
                        media_type="video",
                        duration=video.get("duration"),
                        width=video.get("width"),
                        height=video.get("height"),
                        title=title,
                        author=video.get("user", {}).get("name"),
                    )
                )
        else:
            for photo in data.get("photos", []):
                results.append(
                    SearchResult(
                        id=str(photo["id"]),
                        url=photo.get("src", {}).get("original", ""),
                        preview_url=photo.get("src", {}).get("medium"),
                        provider="pexels",
                        media_type="image",
                        width=photo.get("width"),
                        height=photo.get("height"),
                        title=photo.get("alt"),
                        author=photo.get("photographer"),
                    )
                )

        return results

    async def _search_pixabay(
        self, query: str, media_type: Literal["video", "image"], limit: int
    ) -> list[SearchResult]:
        """Search Pixabay for videos or images."""
        api_key = self._get_pixabay_key()
        client = await self._get_client()

        # Pixabay requires per_page minimum of 3
        per_page = max(limit, 3)

        if media_type == "video":
            url = self.PIXABAY_VIDEO_URL
        else:
            url = self.PIXABAY_IMAGE_URL

        params = {"key": api_key, "q": query, "per_page": per_page}

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise SearchError(f"Pixabay API error: {e}") from e

        results = []
        hits = data.get("hits", [])[:limit]  # Respect original limit

        if media_type == "video":
            for hit in hits:
                videos = hit.get("videos", {})
                # Prefer large, then medium quality
                video_data = videos.get("large") or videos.get("medium") or {}

                results.append(
                    SearchResult(
                        id=str(hit["id"]),
                        url=video_data.get("url", ""),
                        preview_url=video_data.get("thumbnail"),
                        provider="pixabay",
                        media_type="video",
                        duration=hit.get("duration"),
                        width=video_data.get("width"),
                        height=video_data.get("height"),
                        title=hit.get("tags"),
                        author=hit.get("user"),
                    )
                )
        else:
            for hit in hits:
                results.append(
                    SearchResult(
                        id=str(hit["id"]),
                        url=hit.get("largeImageURL", ""),
                        preview_url=hit.get("previewURL"),
                        provider="pixabay",
                        media_type="image",
                        width=hit.get("imageWidth"),
                        height=hit.get("imageHeight"),
                        title=hit.get("tags"),
                        author=hit.get("user"),
                    )
                )

        return results

    async def _search_jamendo(self, query: str, limit: int) -> list[SearchResult]:
        """Search Jamendo for music tracks."""
        client_id = self._get_jamendo_client_id()
        client = await self._get_client()

        params = {
            "client_id": client_id,
            "search": query,
            "limit": limit,
            "format": "json",
        }

        try:
            response = await client.get(self.JAMENDO_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise SearchError(f"Jamendo API error: {e}") from e

        results = []
        for track in data.get("results", []):
            results.append(
                SearchResult(
                    id=str(track["id"]),
                    url=track.get("audiodownload", ""),
                    preview_url=track.get("audio"),
                    provider="jamendo",
                    media_type="audio",
                    duration=track.get("duration"),
                    title=track.get("name"),
                    author=track.get("artist_name"),
                )
            )

        return results

    def _select_best_video_file(
        self, video_files: list[dict]
    ) -> Optional[dict]:
        """Select the best quality video file, preferring 1080p."""
        if not video_files:
            return None

        # Sort by height descending, but prefer 1080p if available
        sorted_files = sorted(
            video_files, key=lambda x: x.get("height", 0), reverse=True
        )

        # Try to find 1080p first
        for vf in sorted_files:
            if vf.get("height") == 1080:
                return vf

        # Otherwise return highest quality
        return sorted_files[0] if sorted_files else None

    def _extract_pexels_title(self, url: str) -> Optional[str]:
        """Extract title from Pexels video URL slug."""
        if not url:
            return None
        # URL format: https://www.pexels.com/video/description-slug-12345/
        match = re.search(r"/video/([^/]+)-\d+/?$", url)
        if match:
            slug = match.group(1)
            return slug.replace("-", " ").title()
        return None

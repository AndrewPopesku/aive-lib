# Add Search Capabilities (Pexels, Pixabay, Jamendo)

Add search and download capabilities to the `aive` MCP server, allowing agents to find and use stock footage (video, images) and music from Pexels, Pixabay, and Jamendo.

## User Review Required

> [!IMPORTANT]
> This implementation requires valid API keys for Pexels, Pixabay, and Jamendo.
> The server will look for `PEXELS_API_KEY`, `PIXABAY_API_KEY`, and `JAMENDO_CLIENT_ID` environment variables.
> Missing keys will raise a `SearchConfigError` with a clear message.

## Implementation Steps

### Step 1: Add Dependencies

**[MODIFY]** [pyproject.toml](../pyproject.toml)
- Add `httpx>=0.27.0` to `dependencies`
- Add `aiofiles>=24.1.0` for async file downloads

### Step 2: Add Error Classes

**[MODIFY]** [src/aive/errors.py](../src/aive/errors.py)
- Add `SearchError(aiveError)` - base for search-related errors
- Add `SearchConfigError(SearchError)` - raised when API keys are missing

### Step 3: Add SearchResult Model

**[MODIFY]** [src/aive/models.py](../src/aive/models.py)
- Add `SearchResult` Pydantic model:

```python
class SearchResult(BaseModel):
    """Represents a search result from a media provider."""
    id: str
    url: str  # download URL
    preview_url: Optional[str] = None
    provider: Literal["pexels", "pixabay", "jamendo"]
    media_type: Literal["video", "image", "audio"]
    duration: Optional[float] = None  # seconds, for video/audio
    width: Optional[int] = None
    height: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
```

### Step 4: Create Search Service

**[NEW]** `src/aive/services/__init__.py`
- Empty init file to create services package

**[NEW]** `src/aive/services/search.py`
- Create async `SearchService` class with:
  - `__init__(cache_dir: Path)` - configurable download cache directory
  - `async search_media(query, provider, media_type, limit) -> list[SearchResult]`
  - `async search_music(query, limit) -> list[SearchResult]`
  - `async download(result: SearchResult) -> Path` - downloads to cache, returns local path
  - Private methods for each API:
    - `_search_pexels(query, media_type, limit)`
    - `_search_pixabay(query, media_type, limit)`
    - `_search_jamendo(query, limit)`
- Use `httpx.AsyncClient` for all HTTP requests
- Validate API keys on first use, raise `SearchConfigError` if missing
- Cache downloaded files by `{provider}_{id}.{ext}` to avoid re-downloads

### Step 5: Integrate with Manager

**[MODIFY]** [src/aive/manager.py](../src/aive/manager.py)
- Add `SearchService` as optional component (lazy-initialized)
- Add methods:
  - `async search_media(query, provider, media_type, limit) -> list[SearchResult]`
  - `async search_music(query, limit) -> list[SearchResult]`
  - `async download_media(result: SearchResult) -> Path`

### Step 6: Register MCP Tools

**[MODIFY]** [src/aive/server/mcp_agent.py](../src/aive/server/mcp_agent.py)

Add 3 new unified tools:

1. **`search_media`** - Search for videos or images
   ```
   Parameters:
   - query: str (required) - Search query
   - provider: "pexels" | "pixabay" (required)
   - media_type: "video" | "image" (required)
   - limit: int (default: 10, max: 50)

   Returns: List of SearchResult with id, url, preview_url, dimensions, etc.
   ```

2. **`search_music`** - Search for music tracks
   ```
   Parameters:
   - query: str (required) - Search query
   - limit: int (default: 10, max: 50)

   Returns: List of SearchResult from Jamendo
   ```

3. **`download_media`** - Download a search result to local cache
   ```
   Parameters:
   - provider: str (required) - Provider name
   - media_id: str (required) - ID from search result
   - url: str (required) - Download URL from search result

   Returns: Local file path (can be used directly with add_clip)
   ```

### Step 7: Add Tests

**[NEW]** `tests/test_search.py`
- Unit tests for `SearchService` with mocked `httpx` responses
- Test cases:
  - Pexels video/image search parsing
  - Pixabay video/image search parsing
  - Jamendo music search parsing
  - Download to cache
  - Missing API key error
  - API error handling (rate limits, invalid responses)

### Step 8: Add Example

**[NEW]** `examples/search_demo.py`
- Demonstrate complete workflow:
  1. Search for background video on Pexels
  2. Search for music on Jamendo
  3. Download both
  4. Create project and add as clips
  5. Render final video

---

## API Response Mapping

### Pexels Videos API

**Endpoint:** `GET https://api.pexels.com/videos/search?query={query}&per_page={limit}`
**Auth:** `Authorization: {PEXELS_API_KEY}` header

**Response Structure:**
```json
{
  "page": 1,
  "per_page": 2,
  "videos": [
    {
      "id": 27095078,
      "width": 3840,
      "height": 2160,
      "duration": 5,
      "url": "https://www.pexels.com/video/...",
      "image": "https://images.pexels.com/videos/.../preview.jpeg",
      "user": {
        "name": "Author Name"
      },
      "video_files": [
        {
          "id": 12070224,
          "quality": "hd",
          "file_type": "video/mp4",
          "width": 1920,
          "height": 1080,
          "link": "https://videos.pexels.com/video-files/.../1920_1080_30fps.mp4"
        }
      ]
    }
  ]
}
```

**Mapping to SearchResult:**
| SearchResult Field | Pexels Field |
|-------------------|--------------|
| `id` | `str(video["id"])` |
| `url` | Best quality from `video["video_files"]` → `link` (prefer 1080p) |
| `preview_url` | `video["image"]` |
| `provider` | `"pexels"` |
| `media_type` | `"video"` |
| `duration` | `video["duration"]` |
| `width` | `video["width"]` |
| `height` | `video["height"]` |
| `title` | Extract from `video["url"]` (slug) |
| `author` | `video["user"]["name"]` |

---

### Pexels Photos API

**Endpoint:** `GET https://api.pexels.com/v1/search?query={query}&per_page={limit}`
**Auth:** `Authorization: {PEXELS_API_KEY}` header

**Response Structure:**
```json
{
  "photos": [
    {
      "id": 20727530,
      "width": 4000,
      "height": 6000,
      "photographer": "Alex Ravvas",
      "alt": "Description of the photo",
      "src": {
        "original": "https://images.pexels.com/photos/.../pexels-photo.jpeg",
        "large2x": "https://images.pexels.com/photos/...?h=650&w=940",
        "medium": "https://images.pexels.com/photos/...?h=350"
      }
    }
  ]
}
```

**Mapping to SearchResult:**
| SearchResult Field | Pexels Field |
|-------------------|--------------|
| `id` | `str(photo["id"])` |
| `url` | `photo["src"]["original"]` |
| `preview_url` | `photo["src"]["medium"]` |
| `provider` | `"pexels"` |
| `media_type` | `"image"` |
| `duration` | `None` |
| `width` | `photo["width"]` |
| `height` | `photo["height"]` |
| `title` | `photo["alt"]` |
| `author` | `photo["photographer"]` |

---

### Pixabay Videos API

**Endpoint:** `GET https://pixabay.com/api/videos/?key={key}&q={query}&per_page={limit}`
**Auth:** `key` query parameter
**Note:** `per_page` minimum is 3, maximum is 200

**Response Structure:**
```json
{
  "total": 43432,
  "totalHits": 500,
  "hits": [
    {
      "id": 111204,
      "pageURL": "https://pixabay.com/videos/id-111204/",
      "tags": "sunset, nature, sky",
      "duration": 16,
      "user": "Username",
      "videos": {
        "large": {
          "url": "https://cdn.pixabay.com/video/.../large.mp4",
          "width": 2560,
          "height": 1440,
          "thumbnail": "https://cdn.pixabay.com/video/.../large.jpg"
        },
        "medium": {
          "url": "https://cdn.pixabay.com/video/.../medium.mp4",
          "width": 1920,
          "height": 1080
        },
        "small": { ... },
        "tiny": { ... }
      }
    }
  ]
}
```

**Mapping to SearchResult:**
| SearchResult Field | Pixabay Field |
|-------------------|---------------|
| `id` | `str(hit["id"])` |
| `url` | `hit["videos"]["large"]["url"]` (or best available) |
| `preview_url` | `hit["videos"]["large"]["thumbnail"]` |
| `provider` | `"pixabay"` |
| `media_type` | `"video"` |
| `duration` | `hit["duration"]` |
| `width` | `hit["videos"]["large"]["width"]` |
| `height` | `hit["videos"]["large"]["height"]` |
| `title` | `hit["tags"]` (first tag or all) |
| `author` | `hit["user"]` |

---

### Pixabay Images API

**Endpoint:** `GET https://pixabay.com/api/?key={key}&q={query}&per_page={limit}`
**Auth:** `key` query parameter
**Note:** `per_page` minimum is 3, maximum is 200

**Response Structure:**
```json
{
  "hits": [
    {
      "id": 7373484,
      "pageURL": "https://pixabay.com/photos/...",
      "tags": "landscape, rainbow, tropical",
      "previewURL": "https://cdn.pixabay.com/photo/...150.jpg",
      "webformatURL": "https://pixabay.com/get/..._640.jpg",
      "largeImageURL": "https://pixabay.com/get/..._1280.jpg",
      "imageWidth": 3150,
      "imageHeight": 2100,
      "user": "Kanenori"
    }
  ]
}
```

**Mapping to SearchResult:**
| SearchResult Field | Pixabay Field |
|-------------------|---------------|
| `id` | `str(hit["id"])` |
| `url` | `hit["largeImageURL"]` |
| `preview_url` | `hit["previewURL"]` |
| `provider` | `"pixabay"` |
| `media_type` | `"image"` |
| `duration` | `None` |
| `width` | `hit["imageWidth"]` |
| `height` | `hit["imageHeight"]` |
| `title` | `hit["tags"]` |
| `author` | `hit["user"]` |

---

### Jamendo Tracks API

**Endpoint:** `GET https://api.jamendo.com/v3.0/tracks/?client_id={id}&search={query}&limit={limit}&format=json`
**Auth:** `client_id` query parameter

**Response Structure:**
```json
{
  "headers": {
    "status": "success",
    "code": 0,
    "results_count": 2
  },
  "results": [
    {
      "id": "1446611",
      "name": "Great and beautiful view",
      "duration": 245,
      "artist_name": "Giocol",
      "album_name": "Album Name",
      "album_image": "https://usercontent.jamendo.com?type=album&id=407366&width=300",
      "audio": "https://prod-1.storage.jamendo.com/?trackid=1446611&format=mp31",
      "audiodownload": "https://prod-1.storage.jamendo.com/download/track/1446611/mp32/"
    }
  ]
}
```

**Mapping to SearchResult:**
| SearchResult Field | Jamendo Field |
|-------------------|---------------|
| `id` | `track["id"]` |
| `url` | `track["audiodownload"]` (MP3 download) |
| `preview_url` | `track["audio"]` (streaming URL) |
| `provider` | `"jamendo"` |
| `media_type` | `"audio"` |
| `duration` | `track["duration"]` |
| `width` | `None` |
| `height` | `None` |
| `title` | `track["name"]` |
| `author` | `track["artist_name"]` |

---

## File Structure After Implementation

```
src/aive/
├── services/
│   ├── __init__.py
│   └── search.py          # NEW: SearchService
├── models.py              # MODIFIED: +SearchResult
├── errors.py              # MODIFIED: +SearchError, +SearchConfigError
├── manager.py             # MODIFIED: +search methods
└── server/
    └── mcp_agent.py       # MODIFIED: +3 tools

tests/
└── test_search.py         # NEW

examples/
└── search_demo.py         # NEW
```

## Verification Plan

### Automated Tests
```bash
uv run pytest tests/test_search.py -v
```

### Manual Verification
1. Set environment variables:
   ```bash
   export PEXELS_API_KEY="your-key"
   export PIXABAY_API_KEY="your-key"
   export JAMENDO_CLIENT_ID="your-client-id"
   ```

2. Run the example:
   ```bash
   uv run python examples/search_demo.py
   ```

3. Test via MCP server (requires MCP client):
   ```bash
   uv run aive-server
   ```

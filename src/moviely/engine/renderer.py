"""Video rendering engine using MoviePy."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, List
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    vfx,
)
from aive.models import ProjectState, Clip, Track
from aive.errors import RenderError
import logging

logger = logging.getLogger(__name__)


@dataclass
class FlattenedClip:
    """A clip with its computed timeline position."""
    clip: Clip
    start_time: float
    track_index: int
    track: Track


class Renderer:
    """Handles video rendering using MoviePy."""

    def __init__(self):
        """Initialize renderer."""
        self.progress_callback: Optional[Callable[[float], None]] = None

    def set_progress_callback(self, callback: Callable[[float], None]) -> None:
        """Set callback for render progress.

        Args:
            callback: Function that takes progress (0.0 to 1.0)
        """
        self.progress_callback = callback

    def render(
        self,
        project: ProjectState,
        output_path: str,
        codec: str = "libx264",
        audio_codec: str = "libmp3lame",
        preset: str = "medium",
    ) -> Path:
        """Render the project to a video file.

        Args:
            project: Project state to render
            output_path: Output file path
            codec: Video codec (default: libx264)
            audio_codec: Audio codec (default: libmp3lame)
            preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)

        Returns:
            Path to rendered video
        """
        try:
            logger.info(f"Starting render: {output_path}")

            # Create output directory if needed
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Flatten tracks into clips with computed start times
            flattened = self._flatten_tracks(project)

            if not flattened:
                raise RenderError("No clips to render")

            # Build composition
            video_clips = []

            # Create background
            duration = project.get_total_duration()
            background = ColorClip(
                size=project.resolution,
                color=project.background_color,
                duration=duration
            )
            video_clips.append(background)

            # Process clips by track order (lower index = lower layer)
            for fc in flattened:
                try:
                    moviepy_clip = self._create_moviepy_clip(fc.clip, fc.track, project)
                    if moviepy_clip:
                        video_clips.append(moviepy_clip.with_start(fc.start_time))
                except Exception as e:
                    logger.error(f"Failed to process clip {fc.clip.id}: {e}")
                    raise RenderError(f"Failed to process clip {fc.clip.id}: {e}")

            # Compose final video
            final_clip = CompositeVideoClip(video_clips, size=project.resolution)
            final_clip.fps = project.fps

            # Render to file
            logger.info(f"Writing video to {output_path}")
            final_clip.write_videofile(
                str(output_file),
                codec=codec,
                audio_codec=audio_codec,
                fps=project.fps,
                preset=preset,
                logger=None if logger.level > logging.INFO else 'bar',
            )

            # Cleanup
            final_clip.close()
            for clip in video_clips:
                clip.close()

            logger.info(f"Render complete: {output_path}")
            return output_file

        except RenderError:
            raise
        except Exception as e:
            raise RenderError(f"Rendering failed: {e}")

    def _flatten_tracks(self, project: ProjectState) -> List[FlattenedClip]:
        """Flatten track hierarchy into a list of clips with computed start times.

        Clips are returned sorted by track index (layer order), with each clip's
        timeline start time calculated from the sum of preceding clip durations.

        Args:
            project: Project state

        Returns:
            List of FlattenedClip objects with computed start times
        """
        result = []

        for track_index, track in enumerate(project.tracks):
            # Skip invisible tracks
            if not track.visible:
                continue

            current_time = 0.0
            for clip in track.clips:
                # Skip gap clips (they're just spacers)
                if clip.type != "gap":
                    result.append(FlattenedClip(
                        clip=clip,
                        start_time=current_time,
                        track_index=track_index,
                        track=track,
                    ))
                # Always advance time (gaps count for timing)
                current_time += clip.duration

        return result

    def _create_moviepy_clip(self, clip: Clip, track: Track, project: ProjectState):
        """Create a MoviePy clip from a Clip model.

        Args:
            clip: Clip model
            track: Parent track (for track-level properties)
            project: Project state

        Returns:
            MoviePy clip object
        """
        moviepy_clip = None

        if clip.type == "video":
            moviepy_clip = VideoFileClip(clip.source).subclipped(
                clip.media_start, clip.media_start + clip.duration
            )
            # Scale video to fill frame while maintaining aspect ratio
            moviepy_clip = self._scale_to_fill(moviepy_clip, project.resolution)

        elif clip.type == "audio":
            audio = AudioFileClip(clip.source).subclipped(
                clip.media_start, clip.media_start + clip.duration
            )
            # Audio clips need a transparent visual placeholder
            moviepy_clip = ColorClip(
                size=(1, 1),
                color=(0, 0, 0),
                duration=clip.duration
            ).with_opacity(0).with_audio(audio)

        elif clip.type == "image":
            moviepy_clip = ImageClip(clip.source).with_duration(clip.duration)
            # Scale image to fill frame while maintaining aspect ratio
            moviepy_clip = self._scale_to_fill(moviepy_clip, project.resolution)

        elif clip.type == "text":
            # Auto-detect text color based on background brightness
            bg_brightness = sum(project.background_color) / (3 * 255)
            text_color = 'black' if bg_brightness > 0.5 else 'white'

            moviepy_clip = TextClip(
                text=clip.source,
                font_size=70,
                color=text_color,
                size=project.resolution,
                method='caption'
            ).with_duration(clip.duration)

        if moviepy_clip is None:
            return None

        # Apply effects
        for effect in clip.effects:
            moviepy_clip = self._apply_effect(moviepy_clip, effect)

        # Calculate effective volume (clip volume * track volume)
        effective_volume = clip.volume * track.volume

        # Apply volume
        if hasattr(moviepy_clip, 'audio') and moviepy_clip.audio and effective_volume != 1.0:
            moviepy_clip = moviepy_clip.with_volume_scaled(effective_volume)

        return moviepy_clip

    def _scale_to_fill(self, clip, target_size: tuple):
        """Scale a clip to fill the target size, cropping if necessary.

        This maintains aspect ratio and ensures the clip fills the entire
        frame by scaling up and center-cropping any overflow.

        Args:
            clip: MoviePy clip
            target_size: Target (width, height)

        Returns:
            Scaled and cropped clip
        """
        target_w, target_h = target_size
        clip_w, clip_h = clip.size

        # Calculate scale factors for both dimensions
        scale_w = target_w / clip_w
        scale_h = target_h / clip_h

        # Use the larger scale to ensure the clip fills the frame
        scale = max(scale_w, scale_h)

        # Scale the clip
        new_w = int(clip_w * scale)
        new_h = int(clip_h * scale)
        clip = clip.resized((new_w, new_h))

        # Center crop to target size
        x_center = new_w // 2
        y_center = new_h // 2
        x1 = x_center - target_w // 2
        y1 = y_center - target_h // 2

        clip = clip.cropped(x1=x1, y1=y1, x2=x1 + target_w, y2=y1 + target_h)

        return clip

    def _apply_effect(self, clip, effect):
        """Apply an effect to a MoviePy clip.

        Args:
            clip: MoviePy clip
            effect: Effect model

        Returns:
            Modified clip
        """
        params = effect.parameters

        if effect.type == "crop":
            x = params.get('x', 0)
            y = params.get('y', 0)
            width = params.get('width', clip.w)
            height = params.get('height', clip.h)
            clip = clip.crop(x1=x, y1=y, x2=x+width, y2=y+height)

        elif effect.type == "fade":
            fade_in = params.get('fade_in', 0)
            fade_out = params.get('fade_out', 0)
            if fade_in > 0:
                clip = clip.with_effects([vfx.FadeIn(fade_in)])
            if fade_out > 0:
                clip = clip.with_effects([vfx.FadeOut(fade_out)])

        elif effect.type == "resize":
            width = params.get('width')
            height = params.get('height')
            if width and height:
                clip = clip.resize((width, height))
            elif width:
                clip = clip.resize(width=width)
            elif height:
                clip = clip.resize(height=height)

        return clip

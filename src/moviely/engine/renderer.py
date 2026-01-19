"""Video rendering engine using MoviePy."""

from pathlib import Path
from typing import Optional, Callable
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    vfx,
)
from moviely.models import ProjectState, Clip
from moviely.errors import RenderError
import logging

logger = logging.getLogger(__name__)


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
            audio_codec: Audio codec (default: aac)
            preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)
            
        Returns:
            Path to rendered video
        """
        try:
            logger.info(f"Starting render: {output_path}")
            
            # Create output directory if needed
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Build composition
            clips_by_layer = self._organize_clips_by_layer(project)
            video_clips = []
            
            # Create background
            if project.clips:
                duration = project.get_total_duration()
                background = ColorClip(
                    size=project.resolution,
                    color=project.background_color,
                    duration=duration
                )
                video_clips.append(background)
            
            # Process clips by layer
            for layer in sorted(clips_by_layer.keys()):
                for clip in clips_by_layer[layer]:
                    try:
                        moviepy_clip = self._create_moviepy_clip(clip, project)
                        if moviepy_clip:
                            video_clips.append(moviepy_clip.with_start(clip.start))
                    except Exception as e:
                        logger.error(f"Failed to process clip {clip.id}: {e}")
                        raise RenderError(f"Failed to process clip {clip.id}: {e}")
            
            if not video_clips:
                raise RenderError("No clips to render")
            
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
    
    def _organize_clips_by_layer(self, project: ProjectState) -> dict:
        """Organize clips by track layer.
        
        Args:
            project: Project state
            
        Returns:
            Dictionary mapping layer to clips
        """
        layers = {}
        for clip in project.clips:
            if clip.track_layer not in layers:
                layers[clip.track_layer] = []
            layers[clip.track_layer].append(clip)
        return layers
    
    def _create_moviepy_clip(self, clip: Clip, project: ProjectState):
        """Create a MoviePy clip from a Clip model.
        
        Args:
            clip: Clip model
            project: Project state
            
        Returns:
            MoviePy clip object
        """
        moviepy_clip = None
        
        if clip.type == "video":
            moviepy_clip = VideoFileClip(clip.source).subclipped(0, clip.duration)

        elif clip.type == "audio":
            audio = AudioFileClip(clip.source).subclipped(0, clip.duration)
            # Audio clips need a transparent visual placeholder
            # Use a 1x1 transparent clip to avoid blocking video content
            moviepy_clip = ColorClip(
                size=(1, 1),
                color=(0, 0, 0),
                duration=clip.duration
            ).with_opacity(0).with_audio(audio)

        elif clip.type == "image":
            moviepy_clip = ImageClip(clip.source).with_duration(clip.duration)

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
        
        # Apply volume
        if hasattr(moviepy_clip, 'audio') and moviepy_clip.audio and clip.volume != 1.0:
            moviepy_clip = moviepy_clip.with_volume_scaled(clip.volume)
        
        return moviepy_clip
    
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

"""
Caption Styler & ASS Track Generator for Local AI Clipper.
"""

from clipper.domain.models import CaptionStyle, CaptionSegment


class CaptionStyler:
    """Generates ASS style header and formatted script lines."""

    @classmethod
    def get_default_style(cls) -> CaptionStyle:
        return CaptionStyle(
            font_name="Outfit",
            font_size=24,
            primary_color="&H00FFFFFF",  # White
            outline_color="&H00000000",  # Black outline
            back_color="&H80000000",
            bold=True,
            outline_width=2.5,
            alignment=2,  # Bottom center
            margin_v=40,
        )

    @classmethod
    def generate_ass_header(cls, style: CaptionStyle, width: int = 1080, height: int = 1920) -> str:
        return f"""[Script Info]
Title: Local AI Clipper Auto Captions
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style.font_name},{style.font_size},{style.primary_color},&H000000FF,{style.outline_color},{style.back_color},{-1 if style.bold else 0},0,0,0,100,100,0,0,1,{style.outline_width},1.0,{style.alignment},20,20,{style.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

"""
ASS Subtitle File Builder for Local AI Clipper.
Writes formatted ASS subtitle track files for FFmpeg burn-in rendering.
"""

from pathlib import Path
from typing import List
from clipper.domain.models import CaptionSegment, CaptionStyle, RenderPlan


class ASSFileBuilder:
    """Generates ASS subtitle script files and returns FFmpeg filter string."""

    @classmethod
    def format_ass_timestamp(cls, ms: int) -> str:
        """Converts milliseconds to ASS timestamp format H:MM:SS.cs."""
        total_cs = ms // 10
        cs = total_cs % 100
        total_sec = total_cs // 100
        sec = total_sec % 60
        total_min = total_sec // 60
        minutes = total_min % 60
        hours = total_min // 60
        return f"{hours}:{minutes:02d}:{sec:02d}.{cs:02d}"

    @classmethod
    def generate_ass_file(cls, plan: RenderPlan, output_ass_path: Path) -> Path:
        style = plan.caption_style
        width = plan.target_width
        height = plan.target_height

        header = f"""[Script Info]
Title: Local AI Clipper Auto Captions
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style.font_name},{style.font_size},{style.primary_color},&H000000FF,{style.outline_color},{style.back_color},{-1 if style.bold else 0},0,0,0,100,100,0,0,1,{style.outline_width},1.0,{style.alignment},20,20,{style.margin_v},1
Style: TopStyle,{style.font_name},{style.font_size},{style.primary_color},&H000000FF,{style.outline_color},{style.back_color},{-1 if style.bold else 0},0,0,0,100,100,0,0,1,{style.outline_width},1.0,8,20,20,{style.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        dialogue_lines: List[str] = []
        for seg in plan.caption_segments:
            start_ts = cls.format_ass_timestamp(seg.start_ms - plan.start_ms)
            end_ts = cls.format_ass_timestamp(seg.end_ms - plan.start_ms)
            text_escaped = "\\N".join(seg.lines)
            style_name = "TopStyle" if seg.position_vertical == "top" else "Default"
            dialogue_lines.append(
                f"Dialogue: 0,{start_ts},{end_ts},{style_name},,0,0,0,,{text_escaped}"
            )

        full_ass_content = header + "\n".join(dialogue_lines) + "\n"

        output_ass_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(full_ass_content)

        return output_ass_path

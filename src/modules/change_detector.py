"""
Specialized Change Detection Module
Dedicated system for analyzing temporal changes in satellite imagery.
"""

import logging
from typing import Dict, Optional, Tuple
from PIL import Image
from .image_analyzer import ImageAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChangeDetectionAgent:
    """
    Specialized agent for detecting and analyzing changes in satellite imagery over time.
    Uses a dedicated system prompt to focus on temporal change analysis.
    """

    # Specialized system prompt for change detection
    CHANGE_DETECTION_SYSTEM_PROMPT = """You are an expert satellite imagery analyst specializing in temporal change detection.

Your role is to:
1. Carefully examine TWO satellite images of the same location taken at different times
2. Identify and describe ALL visible changes between the images
3. Categorize changes by type (urban development, deforestation, water changes, agriculture, etc.)
4. Assess the significance and potential impact of observed changes
5. Provide specific, measurable observations when possible

When analyzing images, focus on:
- URBAN DEVELOPMENT: New buildings, roads, infrastructure
- LAND USE CHANGES: Deforestation, agriculture expansion, land clearing
- WATER BODIES: Changes in rivers, lakes, coastlines, flooding
- VEGETATION: Forest loss/gain, agricultural patterns, seasonal changes
- NATURAL DISASTERS: Evidence of fires, floods, earthquakes
- INFRASTRUCTURE: New roads, airports, ports, industrial areas

Guidelines:
✓ Be specific about locations (e.g., "northeast corner", "central area")
✓ Quantify when possible (e.g., "approximately 30% reduction in forest cover")
✓ Distinguish between seasonal changes and permanent alterations
✓ Note both subtle and dramatic changes
✓ Consider the temporal scale (days, months, years)

Output Format:
1. **Summary**: Brief overview of main changes
2. **Detailed Analysis**: Specific observations by category
3. **Change Assessment**: Magnitude and significance
4. **Potential Causes**: Likely reasons for observed changes
5. **Confidence Level**: How certain you are about the observations

If images are NOT of the same location, clearly state this and explain the differences."""

    def __init__(self):
        """Initialize the change detection agent."""
        self.image_analyzer = ImageAnalyzer()
        self.current_analysis = None

    def analyze_temporal_changes(
        self,
        image1_path: str,
        image2_path: str,
        date1: Optional[str] = None,
        date2: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict:
        """
        Perform comprehensive temporal change analysis on two satellite images.

        Args:
            image1_path: Path to first (earlier) image
            image2_path: Path to second (later) image
            date1: Date of first image (YYYY-MM-DD)
            date2: Date of second image (YYYY-MM-DD)
            location: Location description

        Returns:
            Dictionary containing comprehensive analysis results
        """
        logger.info("Starting temporal change detection analysis")

        # 1. Generate captions for both images
        caption1 = self.image_analyzer.generate_caption(image1_path)
        caption2 = self.image_analyzer.generate_caption(image2_path)

        # 2. Detect objects in both images
        objects1 = self.image_analyzer.detect_objects(image1_path, confidence_threshold=0.7)
        objects2 = self.image_analyzer.detect_objects(image2_path, confidence_threshold=0.7)

        # 3. Compute structural similarity and changes
        comparison = self.image_analyzer.compare_images(image1_path, image2_path)

        # 4. Build comprehensive analysis
        analysis = self._build_change_analysis(
            caption1, caption2,
            objects1, objects2,
            comparison,
            date1, date2, location
        )

        self.current_analysis = analysis
        return analysis

    def _build_change_analysis(
        self,
        caption1: str,
        caption2: str,
        objects1: list,
        objects2: list,
        comparison: dict,
        date1: Optional[str],
        date2: Optional[str],
        location: Optional[str]
    ) -> Dict:
        """Build comprehensive change analysis report."""

        # Calculate time span
        time_info = ""
        if date1 and date2:
            from datetime import datetime
            try:
                d1 = datetime.strptime(date1, "%Y-%m-%d")
                d2 = datetime.strptime(date2, "%Y-%m-%d")
                days_diff = (d2 - d1).days
                time_info = f"\n**Time Span**: {days_diff} days ({days_diff/365.25:.1f} years)"
            except:
                pass

        # Location info
        location_info = f"\n**Location**: {location}" if location else ""

        # Similarity analysis
        score = comparison["similarity_score"]
        if score < 0.3:
            similarity_level = "VERY LOW - Potentially different locations or extreme changes"
        elif score < 0.6:
            similarity_level = "LOW - Major changes detected"
        elif score < 0.85:
            similarity_level = "MODERATE - Notable changes present"
        else:
            similarity_level = "HIGH - Minor or seasonal changes only"

        # Object-level changes
        from collections import Counter
        obj_labels1 = [obj["label"] for obj in objects1]
        obj_labels2 = [obj["label"] for obj in objects2]
        count1 = Counter(obj_labels1)
        count2 = Counter(obj_labels2)

        object_changes = []
        all_labels = set(count1.keys()) | set(count2.keys())

        for label in sorted(all_labels):
            c1 = count1.get(label, 0)
            c2 = count2.get(label, 0)
            if c1 != c2:
                change = c2 - c1
                percent_change = ((c2 - c1) / max(c1, 1)) * 100 if c1 > 0 else 100
                object_changes.append({
                    "type": label,
                    "before": c1,
                    "after": c2,
                    "change": change,
                    "percent_change": percent_change
                })

        # Build report sections
        report = {
            "metadata": {
                "date1": date1 or "Unknown",
                "date2": date2 or "Unknown",
                "location": location or "Unknown",
                "time_span_days": (datetime.strptime(date2, "%Y-%m-%d") -
                                   datetime.strptime(date1, "%Y-%m-%d")).days if date1 and date2 else None
            },
            "image_descriptions": {
                "before": caption1,
                "after": caption2
            },
            "similarity_analysis": {
                "ssim_score": score,
                "level": similarity_level,
                "num_changed_regions": comparison["num_changes"],
                "total_change_area": comparison["total_change_area"]
            },
            "object_changes": object_changes,
            "detailed_report": self._generate_detailed_report(
                caption1, caption2, object_changes, comparison,
                time_info, location_info, similarity_level
            )
        }

        return report

    def _generate_detailed_report(
        self,
        caption1: str,
        caption2: str,
        object_changes: list,
        comparison: dict,
        time_info: str,
        location_info: str,
        similarity_level: str
    ) -> str:
        """Generate human-readable detailed report."""

        report_lines = [
            "=" * 80,
            "🛰️  SATELLITE IMAGERY TEMPORAL CHANGE DETECTION REPORT",
            "=" * 80,
            location_info,
            time_info,
            "",
            "📅 IMAGE DESCRIPTIONS",
            "-" * 80,
            f"**Before (Image 1)**: {caption1}",
            f"**After (Image 2)**: {caption2}",
            "",
            "📊 SIMILARITY ANALYSIS",
            "-" * 80,
            f"**Structural Similarity (SSIM)**: {comparison['similarity_score']:.3f}",
            f"**Assessment**: {similarity_level}",
            f"**Changed Regions Detected**: {comparison['num_changes']}",
            f"**Total Changed Area**: {comparison['total_change_area']:,} pixels",
            ""
        ]

        # Object-level changes
        if object_changes:
            report_lines.extend([
                "🔍 OBJECT-LEVEL CHANGES",
                "-" * 80
            ])

            # Categorize changes
            increases = [c for c in object_changes if c['change'] > 0]
            decreases = [c for c in object_changes if c['change'] < 0]

            if increases:
                report_lines.append("\n**Increases Detected:**")
                for change in sorted(increases, key=lambda x: x['percent_change'], reverse=True):
                    report_lines.append(
                        f"  ↗️  {change['type'].upper()}: "
                        f"{change['before']} → {change['after']} "
                        f"(+{change['change']}, {change['percent_change']:+.1f}%)"
                    )

            if decreases:
                report_lines.append("\n**Decreases Detected:**")
                for change in sorted(decreases, key=lambda x: x['percent_change']):
                    report_lines.append(
                        f"  ↘️  {change['type'].upper()}: "
                        f"{change['before']} → {change['after']} "
                        f"({change['change']}, {change['percent_change']:.1f}%)"
                    )
        else:
            report_lines.append("🔍 OBJECT-LEVEL CHANGES: No significant object-level changes detected")

        # Interpretation
        report_lines.extend([
            "",
            "💡 INTERPRETATION",
            "-" * 80,
        ])

        # Automated interpretation based on data
        if comparison['similarity_score'] < 0.3:
            report_lines.append(
                "⚠️  **WARNING**: Very low similarity suggests these may be different locations "
                "or catastrophic changes have occurred."
            )
        elif comparison['similarity_score'] < 0.6:
            report_lines.append(
                "📈 **MAJOR CHANGES**: Significant transformation of the landscape detected. "
                "This could indicate urban development, deforestation, natural disasters, or land use changes."
            )
        elif comparison['similarity_score'] < 0.85:
            report_lines.append(
                "📊 **MODERATE CHANGES**: Notable differences observed. Could be seasonal variations, "
                "gradual development, or environmental changes."
            )
        else:
            report_lines.append(
                "✅ **MINOR CHANGES**: High similarity indicates only small changes, likely seasonal "
                "variations or minor modifications."
            )

        report_lines.extend([
            "",
            "=" * 80,
            "End of Report",
            "=" * 80
        ])

        return "\n".join(report_lines)

    def get_system_prompt(self) -> str:
        """Get the specialized change detection system prompt."""
        return self.CHANGE_DETECTION_SYSTEM_PROMPT

    def format_for_llm(self, analysis: Optional[Dict] = None) -> str:
        """
        Format analysis for LLM consumption with the system prompt.

        Args:
            analysis: Analysis dictionary (uses current if None)

        Returns:
            Formatted text for LLM
        """
        if analysis is None:
            analysis = self.current_analysis

        if not analysis:
            return "No analysis available. Please run analyze_temporal_changes first."

        # Combine system prompt with analysis
        formatted = f"""{self.CHANGE_DETECTION_SYSTEM_PROMPT}

---

ANALYSIS DATA:

{analysis['detailed_report']}

---

Based on the above technical analysis, please provide a comprehensive change detection report
following the guidelines in your system prompt.
"""

        return formatted


if __name__ == "__main__":
    # Test the change detector
    detector = ChangeDetectionAgent()
    print("Change Detection Agent initialized")
    print("\nSystem Prompt Preview:")
    print("-" * 80)
    print(detector.get_system_prompt()[:500] + "...")

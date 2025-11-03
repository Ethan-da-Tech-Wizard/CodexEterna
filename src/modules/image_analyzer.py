"""
Image Analysis Module for Satellite Image Change Detection
Handles image captioning, object detection, and change detection using open-source models.
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Optional
from skimage.metrics import structural_similarity as ssim
import logging

# Import transformers for BLIP and DETR
from transformers import (
    BlipProcessor, BlipForConditionalGeneration,
    DetrImageProcessor, DetrForObjectDetection
)
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Handles all image analysis tasks including captioning, detection, and comparison."""

    def __init__(self, device: Optional[str] = None):
        """
        Initialize the image analyzer.

        Args:
            device: Device to run models on ('cuda', 'cpu', or None for auto)
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Using device: {self.device}")

        # Model placeholders
        self.blip_processor = None
        self.blip_model = None
        self.detr_processor = None
        self.detr_model = None

        # Cache for results
        self.caption_cache = {}
        self.objects_cache = {}

    def load_captioning_model(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        """
        Load the BLIP image captioning model.

        Args:
            model_name: Name of the BLIP model to use
        """
        logger.info(f"Loading captioning model: {model_name}")
        self.blip_processor = BlipProcessor.from_pretrained(model_name)
        self.blip_model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
        logger.info("Captioning model loaded successfully")

    def load_detection_model(self, model_name: str = "facebook/detr-resnet-50"):
        """
        Load the DETR object detection model.

        Args:
            model_name: Name of the DETR model to use
        """
        logger.info(f"Loading object detection model: {model_name}")
        self.detr_processor = DetrImageProcessor.from_pretrained(model_name)
        self.detr_model = DetrForObjectDetection.from_pretrained(model_name).to(self.device)
        logger.info("Object detection model loaded successfully")

    def generate_caption(self, image_path: str, use_cache: bool = True) -> str:
        """
        Generate a caption for an image.

        Args:
            image_path: Path to the image file
            use_cache: Whether to use cached results

        Returns:
            Caption string describing the image
        """
        # Check cache
        if use_cache and image_path in self.caption_cache:
            logger.info(f"Using cached caption for {image_path}")
            return self.caption_cache[image_path]

        # Load models if needed
        if self.blip_model is None:
            self.load_captioning_model()

        logger.info(f"Generating caption for: {image_path}")

        # Load and process image
        image = Image.open(image_path).convert("RGB")
        inputs = self.blip_processor(image, return_tensors="pt").to(self.device)

        # Generate caption
        with torch.no_grad():
            outputs = self.blip_model.generate(**inputs, max_length=50)

        caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)

        # Cache result
        self.caption_cache[image_path] = caption

        logger.info(f"Caption: {caption}")
        return caption

    def detect_objects(self, image_path: str, confidence_threshold: float = 0.7,
                       use_cache: bool = True) -> List[Dict[str, any]]:
        """
        Detect objects in an image using DETR.

        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence for detections
            use_cache: Whether to use cached results

        Returns:
            List of detected objects with labels, scores, and boxes
        """
        # Check cache
        cache_key = f"{image_path}_{confidence_threshold}"
        if use_cache and cache_key in self.objects_cache:
            logger.info(f"Using cached objects for {image_path}")
            return self.objects_cache[cache_key]

        # Load models if needed
        if self.detr_model is None:
            self.load_detection_model()

        logger.info(f"Detecting objects in: {image_path}")

        # Load and process image
        image = Image.open(image_path).convert("RGB")
        inputs = self.detr_processor(images=image, return_tensors="pt").to(self.device)

        # Detect objects
        with torch.no_grad():
            outputs = self.detr_model(**inputs)

        # Post-process results
        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
        results = self.detr_processor.post_process_object_detection(
            outputs, threshold=confidence_threshold, target_sizes=target_sizes
        )[0]

        # Extract detections
        detections = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            label_name = self.detr_model.config.id2label[int(label)]
            detections.append({
                "label": label_name,
                "confidence": float(score),
                "box": box.cpu().tolist()
            })

        # Cache result
        self.objects_cache[cache_key] = detections

        logger.info(f"Detected {len(detections)} objects")
        return detections

    def compare_images(self, image1_path: str, image2_path: str,
                       return_diff_image: bool = False) -> Dict[str, any]:
        """
        Compare two images and detect changes.

        Args:
            image1_path: Path to the first (before) image
            image2_path: Path to the second (after) image
            return_diff_image: Whether to return the difference image

        Returns:
            Dictionary containing similarity score, change regions, and optionally diff image
        """
        logger.info(f"Comparing images: {image1_path} vs {image2_path}")

        # Load images
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        if img1 is None or img2 is None:
            raise ValueError("Could not load one or both images")

        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Resize images to match if needed
        if gray1.shape != gray2.shape:
            logger.info("Resizing images to match dimensions")
            height = min(gray1.shape[0], gray2.shape[0])
            width = min(gray1.shape[1], gray2.shape[1])
            gray1 = cv2.resize(gray1, (width, height))
            gray2 = cv2.resize(gray2, (width, height))

        # Compute SSIM
        score, diff = ssim(gray1, gray2, full=True)
        logger.info(f"SSIM similarity score: {score:.4f}")

        # Convert difference to uint8
        diff = (diff * 255).astype("uint8")

        # Threshold the difference image
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Find contours of changed regions
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter and collect significant change regions
        change_regions = []
        min_area = 100  # Minimum area to consider as a change

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                change_regions.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "area": int(area)
                })

        result = {
            "similarity_score": float(score),
            "num_changes": len(change_regions),
            "change_regions": change_regions,
            "total_change_area": sum(r["area"] for r in change_regions)
        }

        if return_diff_image:
            result["diff_image"] = diff

        logger.info(f"Detected {len(change_regions)} change regions")
        return result

    def analyze_differences(self, image1_path: str, image2_path: str,
                            include_objects: bool = True) -> str:
        """
        Comprehensive analysis of differences between two images.

        Args:
            image1_path: Path to the first (before) image
            image2_path: Path to the second (after) image
            include_objects: Whether to include object detection analysis

        Returns:
            Detailed text summary of differences
        """
        logger.info("Performing comprehensive difference analysis")

        # Generate captions
        caption1 = self.generate_caption(image1_path)
        caption2 = self.generate_caption(image2_path)

        # Compare images
        comparison = self.compare_images(image1_path, image2_path)

        # Start building summary
        summary_parts = []
        summary_parts.append("=== IMAGE COMPARISON ANALYSIS ===\n")

        summary_parts.append(f"Image 1 Description: {caption1}")
        summary_parts.append(f"Image 2 Description: {caption2}\n")

        # Structural similarity analysis
        score = comparison["similarity_score"]
        summary_parts.append(f"Structural Similarity (SSIM): {score:.2f}")

        if score < 0.3:
            summary_parts.append("⚠️ VERY LOW SIMILARITY: These images may be of completely different locations or scenes.")
        elif score < 0.6:
            summary_parts.append("📊 MAJOR CHANGES: Significant differences detected between the images.")
        elif score < 0.85:
            summary_parts.append("🔍 MODERATE CHANGES: Notable differences present.")
        else:
            summary_parts.append("✓ MINOR CHANGES: Images are quite similar with only small variations.\n")

        # Change regions
        num_changes = comparison["num_changes"]
        if num_changes > 0:
            total_area = comparison["total_change_area"]
            summary_parts.append(f"\nDetected {num_changes} regions with significant changes")
            summary_parts.append(f"Total changed area: {total_area} pixels")

        # Object detection comparison (if enabled)
        if include_objects:
            try:
                objects1 = self.detect_objects(image1_path)
                objects2 = self.detect_objects(image2_path)

                labels1 = [obj["label"] for obj in objects1]
                labels2 = [obj["label"] for obj in objects2]

                # Count objects
                from collections import Counter
                count1 = Counter(labels1)
                count2 = Counter(labels2)

                # Find new and missing objects
                all_labels = set(count1.keys()) | set(count2.keys())

                changes_detected = False
                for label in all_labels:
                    c1 = count1.get(label, 0)
                    c2 = count2.get(label, 0)
                    if c1 != c2:
                        if not changes_detected:
                            summary_parts.append("\n=== OBJECT-LEVEL CHANGES ===")
                            changes_detected = True
                        diff = c2 - c1
                        if diff > 0:
                            summary_parts.append(f"  + {label}: increased by {diff} (from {c1} to {c2})")
                        else:
                            summary_parts.append(f"  - {label}: decreased by {abs(diff)} (from {c1} to {c2})")

            except Exception as e:
                logger.warning(f"Object detection analysis failed: {e}")
                summary_parts.append("\n(Object detection analysis not available)")

        return "\n".join(summary_parts)

    def clear_cache(self):
        """Clear all cached results."""
        self.caption_cache.clear()
        self.objects_cache.clear()
        logger.info("Cache cleared")


if __name__ == "__main__":
    # Test the analyzer
    analyzer = ImageAnalyzer()
    print("Image Analyzer initialized successfully")

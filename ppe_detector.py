import requests
import base64
import json
from typing import Dict, List, Optional, Tuple
from config import settings
from schemas import PPEDetectionResult, RoboflowResponse, RoboflowDetection
import logging

logger = logging.getLogger(__name__)

class PPEDetector:
    def __init__(self):
        self.api_key = settings.ROBOFLOW_API_KEY
        self.project_id = settings.ROBOFLOW_PROJECT_ID
        self.model_version = settings.ROBOFLOW_MODEL_VERSION
        self.base_url = f"https://detect.roboflow.com/{self.project_id}/{self.model_version}"
        
        # PPE class mappings (adjust based on your Roboflow model)
        self.ppe_classes = {
            'helmet': ['helmet', 'hard_hat', 'safety_helmet'],
            'mask': ['mask', 'face_mask', 'respirator', 'n95'],
            'gloves': ['gloves', 'safety_gloves', 'work_gloves'],
            'jacket': ['jacket', 'safety_jacket', 'high_visibility', 'hi_vis', 'vest']
        }
        
        # Minimum confidence thresholds
        self.confidence_thresholds = {
            'helmet': 0.5,
            'mask': 0.5,
            'gloves': 0.5,
            'jacket': 0.5
        }

    def detect_ppe_from_url(self, image_url: str) -> PPEDetectionResult:
        """Detect PPE from image URL using Roboflow API"""
        try:
            params = {
                'api_key': self.api_key,
                'image': image_url
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            roboflow_data = response.json()
            return self._process_roboflow_response(roboflow_data)
            
        except Exception as e:
            logger.error(f"Error detecting PPE from URL: {str(e)}")
            return PPEDetectionResult()

    def detect_ppe_from_base64(self, image_base64: str) -> PPEDetectionResult:
        """Detect PPE from base64 encoded image using Roboflow API"""
        try:
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            params = {
                'api_key': self.api_key
            }
            
            data = {
                'image': image_base64
            }
            
            response = requests.post(self.base_url, params=params, data=data)
            response.raise_for_status()
            
            roboflow_data = response.json()
            return self._process_roboflow_response(roboflow_data)
            
        except Exception as e:
            logger.error(f"Error detecting PPE from base64: {str(e)}")
            return PPEDetectionResult()

    def detect_ppe_from_file(self, image_path: str) -> PPEDetectionResult:
        """Detect PPE from local image file using Roboflow API"""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            return self.detect_ppe_from_base64(image_data)
            
        except Exception as e:
            logger.error(f"Error detecting PPE from file: {str(e)}")
            return PPEDetectionResult()

    def _process_roboflow_response(self, roboflow_data: Dict) -> PPEDetectionResult:
        """Process Roboflow API response and extract PPE detection results"""
        result = PPEDetectionResult()
        
        if 'predictions' not in roboflow_data:
            logger.warning("No predictions found in Roboflow response")
            return result
        
        predictions = roboflow_data['predictions']
        
        # Process each prediction
        for prediction in predictions:
            class_name = prediction.get('class', '').lower()
            confidence = prediction.get('confidence', 0.0)
            
            # Check which PPE type this prediction belongs to
            for ppe_type, class_variants in self.ppe_classes.items():
                if any(variant in class_name for variant in class_variants):
                    if confidence >= self.confidence_thresholds[ppe_type]:
                        self._update_ppe_result(result, ppe_type, confidence)
        
        # Calculate compliance
        result = self._calculate_compliance(result)
        
        return result

    def _update_ppe_result(self, result: PPEDetectionResult, ppe_type: str, confidence: float):
        """Update PPE detection result based on type and confidence"""
        if ppe_type == 'helmet':
            result.helmet_detected = True
            result.helmet_confidence = max(result.helmet_confidence, confidence)
        elif ppe_type == 'mask':
            result.mask_detected = True
            result.mask_confidence = max(result.mask_confidence, confidence)
        elif ppe_type == 'gloves':
            result.gloves_detected = True
            result.gloves_confidence = max(result.gloves_confidence, confidence)
        elif ppe_type == 'jacket':
            result.jacket_detected = True
            result.jacket_confidence = max(result.jacket_confidence, confidence)

    def _calculate_compliance(self, result: PPEDetectionResult) -> PPEDetectionResult:
        """Calculate overall compliance based on detected PPE items"""
        required_ppe = ['helmet', 'mask', 'gloves', 'jacket']
        detected_ppe = []
        
        if result.helmet_detected:
            detected_ppe.append('helmet')
        if result.mask_detected:
            detected_ppe.append('mask')
        if result.gloves_detected:
            detected_ppe.append('gloves')
        if result.jacket_detected:
            detected_ppe.append('jacket')
        
        # Calculate compliance score (percentage of required PPE detected)
        compliance_score = len(detected_ppe) / len(required_ppe) * 100
        result.compliance_score = compliance_score
        
        # Consider compliant if at least 75% of required PPE is detected
        result.is_compliant = compliance_score >= 75.0
        
        return result

    def get_detection_summary(self, result: PPEDetectionResult) -> Dict[str, any]:
        """Get a summary of the detection results"""
        return {
            'is_compliant': result.is_compliant,
            'compliance_score': result.compliance_score,
            'detected_items': {
                'helmet': {
                    'detected': result.helmet_detected,
                    'confidence': result.helmet_confidence
                },
                'mask': {
                    'detected': result.mask_detected,
                    'confidence': result.mask_confidence
                },
                'gloves': {
                    'detected': result.gloves_detected,
                    'confidence': result.gloves_confidence
                },
                'jacket': {
                    'detected': result.jacket_detected,
                    'confidence': result.jacket_confidence
                }
            },
            'missing_items': self._get_missing_items(result),
            'recommendations': self._get_recommendations(result)
        }

    def _get_missing_items(self, result: PPEDetectionResult) -> List[str]:
        """Get list of missing PPE items"""
        missing = []
        if not result.helmet_detected:
            missing.append('helmet')
        if not result.mask_detected:
            missing.append('mask')
        if not result.gloves_detected:
            missing.append('gloves')
        if not result.jacket_detected:
            missing.append('jacket')
        return missing

    def _get_recommendations(self, result: PPEDetectionResult) -> List[str]:
        """Get safety recommendations based on detection results"""
        recommendations = []
        
        if not result.helmet_detected:
            recommendations.append("Please wear a safety helmet to protect your head from falling objects.")
        
        if not result.mask_detected:
            recommendations.append("Please wear a face mask or respirator to protect against airborne hazards.")
        
        if not result.gloves_detected:
            recommendations.append("Please wear safety gloves to protect your hands from cuts and chemicals.")
        
        if not result.jacket_detected:
            recommendations.append("Please wear a high-visibility safety jacket for better visibility and protection.")
        
        if result.is_compliant:
            recommendations.append("Great job! You are properly equipped with all required PPE.")
        
        return recommendations

# Global detector instance
ppe_detector = PPEDetector()



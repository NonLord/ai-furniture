import cv2
import numpy as np
from typing import Dict, Any

def process_image(image: np.ndarray) -> Dict[str, Any]:
    """
    Process the uploaded room image to extract relevant features.
    
    Args:
        image (np.ndarray): Input image array
    
    Returns:
        Dict[str, Any]: Extracted features and measurements
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Basic feature detection
    features = {
        'edges': edges,
        'dominant_colors': get_dominant_colors(image),
        'room_brightness': calculate_brightness(gray),
        'estimated_space': estimate_space(edges)
    }
    
    return features

def detect_room_features(image: np.ndarray) -> Dict[str, Any]:
    """
    Detect key features in the room image.
    
    Args:
        image (np.ndarray): Input image array
    
    Returns:
        Dict[str, Any]: Detected room features
    """
    # Convert color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Detect windows and doors
    light_regions = detect_light_regions(hsv)
    
    # Detect existing furniture
    furniture = detect_furniture(image)
    
    return {
        'light_sources': light_regions,
        'furniture': furniture,
        'wall_color': get_dominant_colors(image)[0]
    }

def get_dominant_colors(image: np.ndarray, n_colors: int = 3) -> list:
    """
    Extract dominant colors from the image.
    
    Args:
        image (np.ndarray): Input image array
        n_colors (int): Number of dominant colors to extract
    
    Returns:
        list: List of dominant RGB colors
    """
    pixels = image.reshape(-1, 3)
    pixels = np.float32(pixels)
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    
    _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    
    return centers.astype(int).tolist()

def calculate_brightness(gray_image: np.ndarray) -> float:
    """
    Calculate the average brightness of the room.
    
    Args:
        gray_image (np.ndarray): Grayscale image array
    
    Returns:
        float: Average brightness value
    """
    return np.mean(gray_image)

def estimate_space(edges: np.ndarray) -> Dict[str, float]:
    """
    Estimate room space based on edge detection.
    
    Args:
        edges (np.ndarray): Edge detection result
    
    Returns:
        Dict[str, float]: Estimated space measurements
    """
    # Simple space estimation based on edge density
    edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
    
    return {
        'space_score': 1.0 - edge_density,
        'complexity': edge_density
    }

def detect_light_regions(hsv_image: np.ndarray) -> list:
    """
    Detect potential windows and light sources.
    
    Args:
        hsv_image (np.ndarray): HSV color space image
    
    Returns:
        list: Detected light regions
    """
    # Threshold for bright regions
    lower_bound = np.array([0, 0, 200])
    upper_bound = np.array([180, 30, 255])
    
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 100]

def detect_furniture(image: np.ndarray) -> list:
    """
    Detect existing furniture in the room.
    
    Args:
        image (np.ndarray): Input image array
    
    Returns:
        list: Detected furniture regions
    """
    # Basic furniture detection using edge detection and contour analysis
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    furniture = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Filter small contours
            x, y, w, h = cv2.boundingRect(contour)
            furniture.append({
                'position': (x, y),
                'size': (w, h),
                'area': area
            })
    
    return furniture

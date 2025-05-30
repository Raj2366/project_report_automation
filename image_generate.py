from base64 import b64decode
from pathlib import Path
import requests
import os
import uuid
from flask import jsonify
import requests

# Configuration
UPLOAD_FOLDER = "static/generated"
IMAGEPIG_API_KEY = "6d96eb62-4caf-4876-8cb2-b7436e92af9a"
API_URL = "https://api.imagepig.com/flux"

def generate_image(prompt, report_type="college"):
    """
    Generate an image using ImagePig API based on user prompt
    Returns URL of generated image or None if failed
    """
    try:
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Prepare API request
        headers = {"Api-Key": IMAGEPIG_API_KEY}
        payload = {
            "prompt": prompt,
            "style": "professional" if report_type == "college" else "illustrated"
        }
        
        # Make API request
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check response
        if not response.ok:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
        if "image_data" not in response.json():
            print("Invalid API response - missing image_data")
            return None
        
        # Generate unique filename
        filename = f"generated_{report_type}_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save image
        with open(filepath, "wb") as f:
            f.write(b64decode(response.json()["image_data"]))
        
        # Verify file was saved
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            print("Failed to save image file")
            return None
            
        return f"/static/generated/{filename}"
        
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None


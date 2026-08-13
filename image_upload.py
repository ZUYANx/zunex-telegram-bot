import base64
import requests
from models import Session, SKU
from config import IMAGE_API_KEY

def upload_image_to_host(image_path):
    """Upload image to freeimage.host and return URL"""
    try:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        resp = requests.post(
            "https://freeimage.host/api/1/upload",
            data={"key": IMAGE_API_KEY, "action": "upload", "source": data},
            timeout=30
        )
        
        result = resp.json()
        if result.get('status_code') == 200:
            return result.get('image', {}).get('display_url')
        return None
    except Exception as e:
        print(f"Upload error: {e}")
        return None

def upload_sku_image(sku_code, image_path):
    """Upload SKU image and update database"""
    url = upload_image_to_host(image_path)
    if url:
        session = Session()
        sku = session.query(SKU).filter_by(sku=sku_code).first()
        if sku:
            sku.image_url = url
            session.commit()
        session.close()
        return url
    return None
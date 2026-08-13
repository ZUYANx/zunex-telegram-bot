import requests
from config import STEADFAST_BASE_URL, LABEL_SIZE
from database import db

def get_steadfast_credentials():
    """Get API keys from database"""
    api_key = db.get_setting('steadfast_api_key')
    secret_key = db.get_setting('steadfast_secret_key')
    return api_key, secret_key

def send_to_steadfast(order_data):
    """Send order to Steadfast and return status with message"""
    try:
        api_key, secret_key = get_steadfast_credentials()
        
        if not api_key or not secret_key:
            return {
                'status': 'error',
                'message': 'API keys not configured. Send /setup'
            }
        
        prefix = db.get_setting('invoice_prefix')
        if not prefix:
            prefix = 'ZX'
        
        payload = {
            "invoice": f"{prefix}{order_data['order_num']}",
            "recipient_name": order_data['name'],
            "recipient_phone": order_data['phone'],
            "recipient_address": order_data['address'],
            "cod_amount": float(order_data['price']),
            "note": ""
        }
        
        headers = {
            "Api-Key": api_key,
            "Secret-Key": secret_key,
            "Content-Type": "application/json"
        }
        
        resp = requests.post(
            f"{STEADFAST_BASE_URL}/create_order",
            json=payload,
            headers=headers,
            timeout=20
        )
        
        result = resp.json()
        
        # Check if successful
        if result.get('status') == 200:
            consignment = result.get('consignment', {})
            consignment_id = consignment.get('consignment_id', '')
            return {
                'status': 'success',
                'message': 'Order sent to Steadfast',
                'consignment_id': consignment_id,
                'data': result
            }
        else:
            error_msg = result.get('message', 'Unknown error')
            return {
                'status': 'error',
                'message': f'Steadfast error: {error_msg}',
                'data': result
            }
        
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': 'No internet connection. Order saved locally.'
        }
    except Exception as e:
        print(f"Steadfast error: {e}")
        return {
            'status': 'error',
            'message': f'Error: {str(e)}'
        }

def create_label_url(consignment_id):
    """Generate label URL"""
    if consignment_id:
        return f"https://www.steadfast.com.bd/user/consignment/print-label/{consignment_id}?size={LABEL_SIZE}"
    return "N/A"
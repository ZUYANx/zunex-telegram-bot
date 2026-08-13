from database import db
from utils import send_message, send_message_with_keyboard

SETUP_STATES = {}

def handle_setup(chat_id):
    business_name = db.get_setting('business_name')
    
    if business_name:
        msg = "Business Configuration\n\n"
        msg += f"Name: {db.get_setting('business_name')}\n"
        msg += f"Prefix: {db.get_setting('invoice_prefix')}\n"
        msg += f"Starting Order: {db.get_setting('order_start')}\n"
        msg += f"Current Order: {db.get_setting('current_order')}\n"
        msg += f"SKU Mode: {db.get_setting('sku_mode')}\n"
        msg += f"Group: {db.get_setting('report_group')}\n\n"
        msg += "Send /reconfigure to change settings"
        
        send_message(chat_id, msg)
        return
    
    SETUP_STATES[str(chat_id)] = {
        'step': 'business_name',
        'data': {}
    }
    
    send_message(
        chat_id,
        "BUSINESS SETUP\n\n"
        "Step 1/6: Enter Business Name\n"
        "Example: ZUNEX Fashion\n\n"
        "Send /cancel to abort"
    )

def handle_setup_input(chat_id, text):
    state = SETUP_STATES.get(str(chat_id))
    if not state:
        return
    
    step = state['step']
    data = state['data']
    
    if step == 'business_name':
        data['business_name'] = text.strip()
        state['step'] = 'invoice_prefix'
        send_message(
            chat_id,
            f"Business Name: {data['business_name']}\n\n"
            "Step 2/6: Enter Invoice Prefix\n"
            "Example: ZX, AA, SB\n\n"
            "Send /cancel to abort"
        )
    
    elif step == 'invoice_prefix':
        data['invoice_prefix'] = text.strip().upper()
        state['step'] = 'order_start'
        send_message(
            chat_id,
            f"Invoice Prefix: {data['invoice_prefix']}\n\n"
            "Step 3/6: Enter Starting Order Number\n"
            "Example: 1000\n\n"
            "Send /cancel to abort"
        )
    
    elif step == 'order_start':
        try:
            data['order_start'] = int(text.strip())
            state['step'] = 'sku_mode'
            
            # Use JSON format, NOT InlineKeyboardMarkup object
            keyboard = [
                [
                    {"text": "Auto-Generate", "callback_data": "skumode_auto"},
                    {"text": "Manual Entry", "callback_data": "skumode_manual"}
                ],
                [
                    {"text": "No SKU", "callback_data": "skumode_none"}
                ]
            ]
            reply_markup = {"inline_keyboard": keyboard}
            
            send_message_with_keyboard(
                chat_id,
                f"Starting Order: {data['order_start']}\n\n"
                "Step 4/6: Choose SKU Mode\n\n"
                "Auto-Generate: Bot creates SKU from product name\n"
                "Manual Entry: You type SKU yourself\n"
                "No SKU: Orders without SKU\n\n"
                "Select an option:",
                reply_markup
            )
        except:
            send_message(chat_id, "Invalid number. Please enter a valid number:")
    
    elif step == 'report_group':
        data['report_group'] = text.strip()
        state['step'] = 'steadfast_api'
        send_message(
            chat_id,
            f"Report Group: {data['report_group']}\n\n"
            "Step 5/6: Enter Steadfast API Key\n\n"
            "Get from: https://portal.packzy.com/api\n\n"
            "Send /cancel to abort"
        )
    
    elif step == 'steadfast_api':
        data['steadfast_api'] = text.strip()
        state['step'] = 'steadfast_secret'
        send_message(
            chat_id,
            "API Key saved\n\n"
            "Step 6/6: Enter Steadfast Secret Key\n\n"
            "Send /cancel to abort"
        )
    
    elif step == 'steadfast_secret':
        data['steadfast_secret'] = text.strip()
        complete_setup(chat_id, data)

def handle_sku_mode_callback(chat_id, mode):
    state = SETUP_STATES.get(str(chat_id))
    if not state:
        return
    
    data = state['data']
    data['sku_mode'] = mode
    
    state['step'] = 'report_group'
    send_message(
        chat_id,
        f"SKU Mode: {mode}\n\n"
        "Step 5/6: Enter Report Group Username or ID\n"
        "Orders will be sent to this group after confirmation\n\n"
        "Example: @myordersgroup or -100123456789\n\n"
        "Send /cancel to abort"
    )

def complete_setup(chat_id, data):
    db.save_setting('business_name', data['business_name'])
    db.save_setting('invoice_prefix', data['invoice_prefix'])
    db.save_setting('order_start', str(data['order_start']))
    db.save_setting('current_order', str(data['order_start']))
    db.save_setting('sku_mode', data.get('sku_mode', 'auto'))
    db.save_setting('report_group', data.get('report_group', ''))
    db.save_setting('steadfast_api_key', data.get('steadfast_api', ''))
    db.save_setting('steadfast_secret_key', data.get('steadfast_secret', ''))
    
    msg = "SETUP COMPLETE!\n\n"
    msg += f"Business: {data['business_name']}\n"
    msg += f"Prefix: {data['invoice_prefix']}\n"
    msg += f"Starting Order: {data['order_start']}\n"
    msg += f"SKU Mode: {data.get('sku_mode', 'auto')}\n"
    msg += f"Report Group: {data.get('report_group', 'Not set')}\n\n"
    msg += "Bot is ready!\n"
    msg += "Send orders with:\n"
    msg += "Phone:\nAddress:\nSKU:\nQty:\nPrice:\nSize:"
    
    send_message(chat_id, msg)
    
    if str(chat_id) in SETUP_STATES:
        del SETUP_STATES[str(chat_id)]
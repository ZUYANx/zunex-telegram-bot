# main.py - ZUNEX Bot Core (Auto-Detect Orders in Groups)

import os
import re
import time
import requests
from datetime import datetime
from config import API_URL, BOT_TOKEN
from database import db
from parser import parse_order
from steadfast import send_to_steadfast, create_label_url
from utils import send_message, send_message_with_keyboard, delete_message, get_updates, check_internet, wait_for_internet
from setup_handler import handle_setup, handle_setup_input, handle_sku_mode_callback, SETUP_STATES
from image_upload import upload_image_to_host

# ============ GLOBAL STATE ============
PENDING_ORDERS = {}
PENDING_DUP = {}
ADD_STATES = {}
last_update = 0
bot_running = True
BOT_USERNAME = None
GROUP_ORDER_KEYWORDS = ['phone:', 'address:', 'sku:', 'qty:', 'price:', 'name:', 'customer:', 'mobile:']

# ============ GET BOT USERNAME ============

def get_bot_username():
    """Get bot username from Telegram"""
    global BOT_USERNAME
    if BOT_USERNAME:
        return BOT_USERNAME
    
    try:
        bot_info = requests.get(f"{API_URL}/getMe").json()
        if bot_info.get('ok'):
            BOT_USERNAME = bot_info['result']['username']
            db.save_setting('bot_username', BOT_USERNAME)
            return BOT_USERNAME
    except:
        pass
    
    BOT_USERNAME = 'zunex_bot'
    return BOT_USERNAME

# ============ ORDER PROCESSING ============

def process_order(chat_id, text, is_duplicate=False, is_group=False):
    """Process incoming order"""
    
    # Check if business configured
    business_name = db.get_setting('business_name')
    if not business_name:
        send_message(chat_id, "Business not configured. Send /setup to configure.")
        return
    
    order = parse_order(text)
    if not order:
        send_message(
            chat_id,
            "Missing required fields\n\n"
            "Required: Phone and Address\n\n"
            "Example:\n"
            "Phone: 01712345678\n"
            "Address: Dhaka, Bangladesh"
        )
        return
    
    # Auto-generate SKU if needed
    sku_mode = db.get_setting('sku_mode')
    if sku_mode == 'auto' and order['sku'] == 'N/A':
        product_name = order.get('product_name', 'Product')
        new_sku = generate_sku(product_name)
        if new_sku:
            order['sku'] = new_sku
            db.save_sku({
                'sku': new_sku,
                'product_name': product_name,
                'price': order.get('price', 0.0)
            })
    elif sku_mode == 'none':
        order['sku'] = 'N/A'
    
    # Check duplicate
    if order['sku'] != 'N/A' and not is_duplicate:
        dup = db.check_duplicate(order['phone'], order['sku'])
        if dup:
            show_duplicate_warning(chat_id, order, dup)
            return
    
    # Show confirmation
    show_confirmation(chat_id, order)


def generate_sku(product_name):
    """Auto-generate SKU from product name"""
    prefix = db.get_setting('invoice_prefix')
    if not prefix:
        prefix = 'PRD'
    prefix = prefix[:3]
    
    clean_name = re.sub(r'[^A-Z0-9]', '', product_name.upper())
    if len(clean_name) >= 2:
        prefix = clean_name[:3]
    
    existing = db.get_all_skus()
    numbers = []
    for sku in existing:
        if sku.sku.startswith(prefix):
            try:
                num = int(sku.sku.replace(prefix, ''))
                numbers.append(num)
            except:
                pass
    
    next_num = max(numbers) + 1 if numbers else 1
    return f"{prefix}{next_num:03d}"


def show_duplicate_warning(chat_id, order, dup):
    """Show duplicate warning with inline keyboard"""
    callback_id = f"dup_{chat_id}_{int(datetime.now().timestamp())}"
    
    PENDING_DUP[callback_id] = {
        'order': order,
        'chat_id': chat_id,
        'dup_order': dup
    }
    
    msg = "DUPLICATE ORDER DETECTED!\n\n"
    msg += f"Customer: {dup.customer_name}\n"
    msg += f"Phone: {dup.phone}\n"
    msg += f"SKU: {dup.sku}\n"
    msg += f"Order #: {dup.order_num}\n"
    msg += f"Date: {dup.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
    msg += "Place this order anyway?"
    
    keyboard = [
        [
            {"text": "Yes, Place Order", "callback_data": f"dup_yes_{callback_id}"},
            {"text": "No, Cancel", "callback_data": f"dup_no_{callback_id}"}
        ]
    ]
    reply_markup = {"inline_keyboard": keyboard}
    
    send_message_with_keyboard(chat_id, msg, reply_markup)


def handle_duplicate_callback(chat_id, callback_id, confirm):
    """Handle duplicate response"""
    dup_data = PENDING_DUP.get(callback_id)
    
    if not dup_data:
        send_message(chat_id, "Order expired or not found.")
        return
    
    if confirm:
        order = dup_data['order']
        order_text = f"Name: {order.get('name', 'Unknown')}\n"
        order_text += f"Phone: {order['phone']}\n"
        order_text += f"Address: {order['address']}\n"
        order_text += f"SKU: {order['sku']}\n"
        order_text += f"Qty: {order.get('quantity', 1)}\n"
        order_text += f"Price: {order.get('price', 0)}\n"
        order_text += f"Size: {order.get('size', '')}"
        
        process_order(chat_id, order_text, is_duplicate=True)
        send_message(chat_id, "Order placed successfully.")
    else:
        send_message(chat_id, "Order cancelled.")
    
    if callback_id in PENDING_DUP:
        del PENDING_DUP[callback_id]


def show_confirmation(chat_id, order):
    """Show confirmation with inline buttons"""
    callback_id = f"order_{chat_id}_{int(datetime.now().timestamp())}"
    PENDING_ORDERS[callback_id] = {
        'order': order,
        'chat_id': chat_id
    }
    
    msg = "Please Confirm Order\n\n"
    msg += f"Name: {order.get('name', 'Unknown')}\n"
    msg += f"Phone: {order['phone']}\n"
    msg += f"Address: {order['address']}\n"
    
    if order['sku'] != 'N/A':
        msg += f"SKU: {order['sku']}\n"
        msg += f"Size: {order.get('size', 'N/A')}\n"
        msg += f"Quantity: {order.get('quantity', 1)}\n"
    
    msg += f"Price: {order.get('price', 0)} BDT"
    
    if order['sku'] != 'N/A':
        sku_data = db.get_sku(order['sku'])
        if sku_data and sku_data.image_url:
            msg += f"\n\nImage: {sku_data.image_url}"
    
    keyboard = [
        [
            {"text": "Confirm", "callback_data": f"confirm_{callback_id}"},
            {"text": "Cancel", "callback_data": f"cancel_{callback_id}"}
        ]
    ]
    reply_markup = {"inline_keyboard": keyboard}
    
    send_message_with_keyboard(chat_id, msg, reply_markup)


def confirm_order(chat_id, callback_id):
    """Confirm and process order"""
    order_data = PENDING_ORDERS.get(callback_id)
    
    if not order_data:
        send_message(chat_id, "Order expired or not found.")
        return
    
    order = order_data['order']
    
    if order['sku'] != 'N/A':
        dup = db.check_duplicate(order['phone'], order['sku'])
        if dup:
            show_duplicate_warning(chat_id, order, dup)
            if callback_id in PENDING_ORDERS:
                del PENDING_ORDERS[callback_id]
            return
    
    order_num = db.get_next_order_num()
    
    order_data = {
        'order_num': order_num,
        'name': order.get('name', 'Unknown'),
        'phone': order['phone'],
        'address': order['address'],
        'sku': order.get('sku', 'N/A'),
        'product_name': order.get('product_name', ''),
        'quantity': order.get('quantity', 1),
        'size': order.get('size', ''),
        'price': order.get('price', 0.0)
    }
    
    # Send to Steadfast and get status
    result = send_to_steadfast(order_data)
    
    consignment_id = ''
    steadfast_status = ''
    steadfast_message = ''
    
    if result.get('status') == 'success':
        consignment_id = result.get('consignment_id', '')
        steadfast_status = 'SUCCESS'
        steadfast_message = result.get('message', 'Order sent to Steadfast')
        order_data['consignment_id'] = consignment_id
    else:
        steadfast_status = 'FAILED'
        steadfast_message = result.get('message', 'Unknown error')
    
    # Save to database (always save even if Steadfast fails)
    saved_order = db.save_order(order_data)
    
    # Send to report group
    send_to_report_group(order_data, saved_order.id)
    
    # Build confirmation message
    confirm = f"Order #{order_num} Confirmed\n\n"
    confirm += f"Name: {order_data['name']}\n"
    confirm += f"Phone: {order_data['phone']}\n"
    confirm += f"Address: {order_data['address']}\n"
    confirm += f"Price: {order_data['price']} BDT\n"
    
    if order_data['sku'] != 'N/A':
        confirm += f"SKU: {order_data['sku']}\n"
        confirm += f"Qty: {order_data['quantity']}\n"
        confirm += f"Size: {order_data['size'] or 'N/A'}\n"
    
    # Show Steadfast status
    confirm += f"\nSteadfast: {steadfast_status}"
    if steadfast_message:
        confirm += f"\n{steadfast_message}"
    
    if consignment_id:
        label_url = create_label_url(consignment_id)
        confirm += f"\nLabel: {label_url}"
    
    send_message(chat_id, confirm)
    
    if callback_id in PENDING_ORDERS:
        del PENDING_ORDERS[callback_id]


def handle_cancel_order(chat_id, callback_id):
    """Cancel order"""
    if callback_id in PENDING_ORDERS:
        del PENDING_ORDERS[callback_id]
    send_message(chat_id, "Order Cancelled")


def send_to_report_group(order_data, order_id):
    """Send order to report group"""
    report_group = db.get_setting('report_group')
    if not report_group:
        return
    
    image_url = ''
    if order_data['sku'] != 'N/A':
        sku_data = db.get_sku(order_data['sku'])
        if sku_data and sku_data.image_url:
            image_url = sku_data.image_url
    
    msg = "New Order Received\n\n"
    msg += f"Order #: {order_data['order_num']}\n"
    msg += f"Name: {order_data['name']}\n"
    msg += f"Phone: {order_data['phone']}\n"
    msg += f"Address: {order_data['address']}\n"
    msg += f"Price: {order_data['price']} BDT\n"
    
    if order_data['sku'] != 'N/A':
        msg += f"SKU: {order_data['sku']}\n"
        msg += f"Qty: {order_data['quantity']}\n"
        msg += f"Size: {order_data['size'] or 'N/A'}\n"
    
    if image_url:
        msg += f"\nImage: {image_url}"
    
    if order_data.get('consignment_id'):
        label_url = create_label_url(order_data['consignment_id'])
        msg += f"\nLabel: {label_url}"
    
    send_message(report_group, msg)
    db.mark_order_sent(order_id)


# ============ COMMAND HANDLERS ============

def handle_start(chat_id):
    business_name = db.get_setting('business_name')
    if not business_name:
        send_message(chat_id, "Send /setup to configure this bot.")
        return
    
    msg = f"Welcome to {business_name} Bot\n\n"
    msg += "Send your order with:\n"
    msg += "Phone:\nAddress:\nSKU:\nQty:\nPrice:\nSize:\n\n"
    msg += "Commands:\n"
    msg += "/today - Today's orders\n"
    msg += "/sr - Search orders\n"
    msg += "/sku - View product details\n"
    msg += "/add - Add new product\n"
    msg += "/setup - Configure bot"
    
    send_message(chat_id, msg)


def handle_today(chat_id):
    orders = db.get_today_orders()
    
    if not orders:
        send_message(chat_id, "No orders today.")
        return
    
    total = sum(o.price for o in orders)
    msg = f"Today's Orders: {len(orders)} | Total: {total} BDT\n\n"
    
    for o in orders[:10]:
        size_info = f" | Size: {o.size}" if o.size else ""
        msg += f"#{o.order_num} | {o.customer_name} | {o.sku} | {o.quantity}x{size_info} | {o.price} BDT\n"
    
    if len(orders) > 10:
        msg += f"\n... and {len(orders) - 10} more"
    
    send_message(chat_id, msg)


def handle_search(chat_id, query):
    if not query:
        send_message(chat_id, "Usage: /sr ORDER_NUM or PHONE")
        return
    
    results = db.search_orders(query)
    if not results:
        send_message(chat_id, f"No results for: {query}")
        return
    
    for r in results:
        size_info = f" | Size: {r.size}" if r.size else ""
        label = create_label_url(r.consignment_id) if r.consignment_id else "N/A"
        msg = f"Order #{r.order_num}\n"
        msg += f"{r.customer_name}\n"
        msg += f"{r.phone}\n"
        msg += f"{r.sku} | Qty: {r.quantity}{size_info} | {r.price} BDT\n"
        msg += f"Label: {label}"
        send_message(chat_id, msg)


def handle_sku_info(chat_id, sku_code):
    if not sku_code:
        send_message(chat_id, "Usage: /sku SKU_CODE")
        return
    
    sku = db.get_sku(sku_code.upper())
    if not sku:
        send_message(chat_id, f"SKU {sku_code} not found.")
        return
    
    msg = f"SKU: {sku.sku}\n"
    msg += f"Product: {sku.product_name}\n"
    msg += f"Price: {sku.price} {sku.currency}\n"
    msg += f"Sizes: {sku.sizes}\n"
    msg += f"Category: {sku.category or 'N/A'}\n"
    msg += f"Brand: {sku.brand or 'N/A'}\n"
    
    if sku.image_url:
        msg += f"\nImage: {sku.image_url}"
    
    send_message(chat_id, msg)


def handle_add_sku(chat_id):
    ADD_STATES[str(chat_id)] = {'step': 'sku_code', 'data': {}}
    send_message(
        chat_id,
        "Add New Product\n\n"
        "Step 1/5: Enter SKU Code\n"
        "Example: ZX-001\n\n"
        "Send /cancel to abort"
    )


def handle_add_sku_input(chat_id, text, photo_file_id=None):
    state = ADD_STATES.get(str(chat_id))
    if not state:
        return
    
    step = state['step']
    data = state['data']
    
    if step == 'sku_code':
        data['sku'] = text.strip().upper()
        state['step'] = 'product_name'
        send_message(chat_id, f"SKU: {data['sku']}\n\nStep 2/5: Enter Product Name")
    
    elif step == 'product_name':
        data['product_name'] = text.strip()
        state['step'] = 'price'
        send_message(chat_id, f"Product: {data['product_name']}\n\nStep 3/5: Enter Price\nExample: 1099")
    
    elif step == 'price':
        try:
            data['price'] = float(text.strip())
            state['step'] = 'sizes'
            send_message(chat_id, f"Price: {data['price']} BDT\n\nStep 4/5: Enter Sizes\nExample: 36,38,40,42,44,46\nOr type 'skip' for no sizes")
        except:
            send_message(chat_id, "Invalid price. Enter a number:")
    
    elif step == 'sizes':
        if text.strip().lower() == 'skip':
            data['sizes'] = ''
        else:
            data['sizes'] = text.strip()
        state['step'] = 'image'
        send_message(chat_id, f"Sizes: {data['sizes'] or 'None'}\n\nStep 5/5: Send Product Image (photo)\nOr type 'skip' for no image")
    
    elif step == 'image':
        if photo_file_id:
            image_url = handle_product_image(photo_file_id, data['sku'])
            data['image_url'] = image_url
        else:
            data['image_url'] = ''
        
        save_new_sku(chat_id, data)
        return


def handle_product_image(file_id, sku_code):
    try:
        file_info = requests.get(f"{API_URL}/getFile?file_id={file_id}").json()
        if file_info['ok']:
            file_path = file_info['result']['file_path']
            img_data = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}").content
            
            temp_path = f"/tmp/{sku_code}.jpg"
            with open(temp_path, 'wb') as f:
                f.write(img_data)
            
            image_url = upload_image_to_host(temp_path)
            
            try:
                os.remove(temp_path)
            except:
                pass
            
            return image_url
    except Exception as e:
        print(f"Image upload error: {e}")
    
    return ''


def save_new_sku(chat_id, data):
    sku_data = {
        'sku': data['sku'],
        'product_name': data['product_name'],
        'price': data['price'],
        'sizes': data.get('sizes', ''),
        'image_url': data.get('image_url', ''),
        'currency': 'BDT',
        'category': '',
        'brand': ''
    }
    
    db.save_sku(sku_data)
    
    msg = "Product Added Successfully!\n\n"
    msg += f"SKU: {data['sku']}\n"
    msg += f"Product: {data['product_name']}\n"
    msg += f"Price: {data['price']} BDT\n"
    msg += f"Sizes: {data.get('sizes', 'None')}\n"
    
    if data.get('image_url'):
        msg += f"\nImage: {data['image_url']}"
    
    send_message(chat_id, msg)
    
    if str(chat_id) in ADD_STATES:
        del ADD_STATES[str(chat_id)]


def is_order_message(text):
    """Check if message looks like an order"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check for order keywords
    order_keywords = ['phone:', 'address:', 'sku:', 'qty:', 'price:', 'name:', 'customer:', 'mobile:']
    if any(keyword in text_lower for keyword in order_keywords):
        return True
    
    # Check if it has phone number (11 digits starting with 01)
    if re.search(r'01\d{9}', text):
        return True
    
    # Check if it has address-like words
    address_words = ['dhaka', 'chittagong', 'rajshahi', 'khulna', 'sylhet', 'barishal', 'rangpur', 'mymensingh', 
                     'house', 'road', 'village', 'union', 'upazila', 'district', 'city', 'street']
    if any(word in text_lower for word in address_words):
        # Also check for price or sku to confirm it's an order
        if re.search(r'\d+', text) and (re.search(r'[A-Z]{2,}-\d+', text) or re.search(r'price|total|tk|bdt', text_lower)):
            return True
    
    return False


# ============ MAIN LOOP ============

print("=" * 40)
print("ZUNEX BOT RUNNING")
print("Commands: /start, /setup, /today, /sr, /sku, /add")
print("Works in: Private Chat and Groups (Auto-Detect Orders)")
print("=" * 40)

# Get bot username
get_bot_username()
print(f"Bot Username: @{BOT_USERNAME}")

# Check internet on startup
if not check_internet():
    print("Waiting for internet connection...")
    wait_for_internet()

while bot_running:
    try:
        # Get updates with internet check
        data = get_updates(last_update)
        
        if data.get('ok') and data.get('result'):
            for update in data['result']:
                last_update = update['update_id']
                
                # Handle messages
                if 'message' in update:
                    msg = update['message']
                    chat_id = msg['chat']['id']
                    text = msg.get('text', '')
                    chat_type = msg.get('chat', {}).get('type', 'private')
                    
                    # Check if this is a group/supergroup
                    is_group = chat_type in ['group', 'supergroup']
                    
                    # ============ COMMAND HANDLING ============
                    if text.startswith('/'):
                        parts = text[1:].split(maxsplit=1)
                        cmd = parts[0].lower()
                        arg = parts[1] if len(parts) > 1 else ''
                        
                        # Commands that work in groups
                        if cmd == 'start':
                            handle_start(chat_id)
                        elif cmd == 'setup':
                            if is_group:
                                send_message(chat_id, "Setup can only be done in private chat. Please message me directly.")
                            else:
                                handle_setup(chat_id)
                        elif cmd == 'today':
                            handle_today(chat_id)
                        elif cmd == 'sr':
                            handle_search(chat_id, arg)
                        elif cmd == 'sku':
                            handle_sku_info(chat_id, arg)
                        elif cmd == 'add':
                            if is_group:
                                send_message(chat_id, "Add product can only be done in private chat. Please message me directly.")
                            else:
                                handle_add_sku(chat_id)
                        elif cmd == 'cancel':
                            if str(chat_id) in ADD_STATES:
                                del ADD_STATES[str(chat_id)]
                                send_message(chat_id, "Operation cancelled.")
                            elif str(chat_id) in SETUP_STATES:
                                del SETUP_STATES[str(chat_id)]
                                send_message(chat_id, "Setup cancelled.")
                        elif cmd == 'reconfigure':
                            if is_group:
                                send_message(chat_id, "Reconfigure can only be done in private chat. Please message me directly.")
                            else:
                                if str(chat_id) in SETUP_STATES:
                                    del SETUP_STATES[str(chat_id)]
                                SETUP_STATES[str(chat_id)] = {
                                    'step': 'business_name',
                                    'data': {}
                                }
                                send_message(chat_id, "Reconfiguration started.\n\nStep 1/6: Enter Business Name")
                        else:
                            send_message(chat_id, "Commands: /start, /setup, /today, /sr, /sku, /add")
                        continue
                    
                    # ============ PRIVATE CHAT PROCESSING ============
                    if not is_group:
                        # Handle ADD SKU states (private only)
                        if str(chat_id) in ADD_STATES:
                            state = ADD_STATES[str(chat_id)]
                            if 'photo' in msg and state['step'] == 'image':
                                file_id = msg['photo'][-1]['file_id']
                                handle_add_sku_input(chat_id, 'image', photo_file_id=file_id)
                                continue
                            if text.lower() == 'skip' and state['step'] == 'image':
                                handle_add_sku_input(chat_id, 'skip')
                                continue
                            handle_add_sku_input(chat_id, text)
                            continue
                        
                        # Handle SETUP states (private only)
                        if str(chat_id) in SETUP_STATES:
                            handle_setup_input(chat_id, text)
                            continue
                        
                        # Process order in private chat (always detect)
                        if text and is_order_message(text):
                            process_order(chat_id, text, is_group=False)
                    
                    # ============ GROUP CHAT PROCESSING ============
                    else:
                        # In groups, only process if it looks like an order
                        if text and is_order_message(text):
                            # Don't process if it's a command
                            if not text.startswith('/'):
                                # Check if business is configured
                                business_name = db.get_setting('business_name')
                                if business_name:
                                    process_order(chat_id, text, is_group=True)
                                else:
                                    # Bot not configured, send a message to setup
                                    send_message(chat_id, "Bot not configured. Please setup first in private chat using /setup")
                
                # ============ HANDLE CALLBACK QUERIES ============
                elif 'callback_query' in update:
                    query = update['callback_query']
                    data = query['data']
                    chat_id = query['message']['chat']['id']
                    message_id = query['message']['message_id']
                    
                    # Confirm order
                    if data.startswith('confirm_'):
                        callback_id = data.replace('confirm_', '')
                        confirm_order(chat_id, callback_id)
                        try:
                            delete_message(chat_id, message_id)
                        except:
                            pass
                    
                    # Cancel order
                    elif data.startswith('cancel_'):
                        callback_id = data.replace('cancel_', '')
                        handle_cancel_order(chat_id, callback_id)
                        try:
                            delete_message(chat_id, message_id)
                        except:
                            pass
                    
                    # Duplicate - Yes
                    elif data.startswith('dup_yes_'):
                        callback_id = data.replace('dup_yes_', '')
                        handle_duplicate_callback(chat_id, callback_id, confirm=True)
                        try:
                            delete_message(chat_id, message_id)
                        except:
                            pass
                    
                    # Duplicate - No
                    elif data.startswith('dup_no_'):
                        callback_id = data.replace('dup_no_', '')
                        handle_duplicate_callback(chat_id, callback_id, confirm=False)
                        try:
                            delete_message(chat_id, message_id)
                        except:
                            pass
                    
                    # SKU mode selection
                    elif data.startswith('skumode_'):
                        mode = data.replace('skumode_', '')
                        handle_sku_mode_callback(chat_id, mode)
                        try:
                            delete_message(chat_id, message_id)
                        except:
                            pass
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        bot_running = False
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)

print("Bot stopped.")
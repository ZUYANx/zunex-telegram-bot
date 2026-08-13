import re

FIELD_ALIASES = {
    'name': ['name', 'customer', 'buyer', 'client', 'recipient'],
    'phone': ['phone', 'mobile', 'cell', 'whatsapp', 'contact'],
    'address': ['address', 'addr', 'location', 'house', 'village', 'road', 'district', 'city'],
    'sku': ['sku', 'product', 'item', 'code', 'product code'],
    'quantity': ['qty', 'quantity', 'quant', 'pieces', 'pcs', 'unit', 'amount'],
    'price': ['price', 'total', 'amount', 'cost', 'tk', 'taka', 'bdt'],
    'size': ['size', 'sizes', 'body', 'chest', 'length']
}

def parse_order(text):
    """Extract fields from order text"""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    
    extracted = {}
    
    # Line-by-line scanning
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        for field, aliases in FIELD_ALIASES.items():
            if extracted.get(field):
                continue
            
            for alias in aliases:
                patterns = [
                    rf'{alias}\s*[:;：;\-–—]\s*(.+)',
                    rf'{alias}\s+(.+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        extracted[field] = match.group(1).strip()
                        break
                if extracted.get(field):
                    break
    
    # Position-based fallback
    if not extracted:
        extracted = extract_by_position(lines)
    
    # Clean fields
    extracted = clean_extracted(extracted)
    
    # Validate: only phone and address required
    if not extracted.get('phone') or not extracted.get('address'):
        return None
    
    # Set defaults
    extracted.setdefault('name', 'Unknown')
    extracted.setdefault('sku', 'N/A')
    extracted.setdefault('quantity', 1)
    extracted.setdefault('price', 0.0)
    extracted.setdefault('size', '')
    
    return extracted

def extract_by_position(lines):
    """Extract by position when no labels"""
    result = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Phone detection
        if re.search(r'01\d{9}', line) and not result.get('phone'):
            result['phone'] = line
        
        # SKU detection
        elif re.search(r'[A-Z]{2,}-\d{3,}', line) and not result.get('sku'):
            result['sku'] = line
        
        # Price detection
        elif re.match(r'^\d+(\.\d+)?$', line) and not result.get('price'):
            num = float(line)
            if num > 100:
                result['price'] = line
            elif num <= 100 and not result.get('quantity'):
                result['quantity'] = line
        
        # Quantity detection
        elif re.match(r'^\d+$', line) and not result.get('quantity'):
            num = int(line)
            if 1 <= num <= 100:
                result['quantity'] = line
    
    # Fill remaining by position
    fields = ['name', 'phone', 'address', 'sku', 'quantity', 'price', 'size']
    remaining = [f for f in fields if f not in result]
    position = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if position < len(remaining):
            result[remaining[position]] = line
            position += 1
    
    return result

def clean_extracted(data):
    """Clean extracted fields"""
    cleaned = data.copy()
    
    # Clean phone
    if 'phone' in cleaned:
        phone = re.sub(r'\D', '', cleaned['phone'])
        if phone.startswith('88'):
            phone = phone[2:]
        if len(phone) == 10:
            phone = '0' + phone
        cleaned['phone'] = phone
    
    # Clean price
    if 'price' in cleaned:
        price = re.sub(r'[^\d.]', '', cleaned['price'])
        try:
            cleaned['price'] = float(price)
        except:
            cleaned['price'] = 0.0
    
    # Clean quantity
    if 'quantity' in cleaned:
        qty = re.sub(r'\D', '', cleaned['quantity'])
        cleaned['quantity'] = int(qty) if qty else 1
    
    return cleaned
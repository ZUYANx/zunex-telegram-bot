# database.py - SQLAlchemy Database Operations

from models import Session, Setting, Order, SKU
from datetime import datetime, timedelta
from config import STARTING_ORDER_NUM

class DatabaseManager:
    def __init__(self):
        self.session = Session()
    
    def close(self):
        self.session.close()
    
    # ============ SETTINGS ============
    def get_setting(self, key):
        """Get setting by key"""
        setting = self.session.query(Setting).filter_by(key=key).first()
        return setting.value if setting else None
    
    def save_setting(self, key, value):
        """Save or update setting"""
        setting = self.session.query(Setting).filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            self.session.add(setting)
        self.session.commit()
        return setting
    
    # ============ ORDERS ============
    def get_next_order_num(self):
        """Get next order number and increment"""
        current = self.get_setting('current_order')
        if not current:
            current = STARTING_ORDER_NUM
        else:
            current = int(current)
        
        next_num = current + 1
        self.save_setting('current_order', str(next_num))
        return next_num
    
    def save_order(self, order_data):
        """Save new order"""
        order = Order(
            order_num=order_data['order_num'],
            customer_name=order_data.get('name', 'Unknown'),
            phone=order_data['phone'],
            address=order_data['address'],
            sku=order_data.get('sku', 'N/A'),
            product_name=order_data.get('product_name', ''),
            quantity=order_data.get('quantity', 1),
            size=order_data.get('size', ''),
            price=order_data.get('price', 0.0),
            consignment_id=order_data.get('consignment_id', '')
        )
        self.session.add(order)
        self.session.commit()
        return order
    
    def get_order_by_num(self, order_num):
        """Get order by number"""
        return self.session.query(Order).filter_by(order_num=order_num).first()
    
    def search_orders(self, query):
        """Search orders by order_num or phone"""
        try:
            query_num = int(query)
            return self.session.query(Order).filter_by(order_num=query_num).all()
        except:
            return self.session.query(Order).filter(Order.phone.like(f'%{query}%')).all()
    
    def get_today_orders(self):
        """Get today's orders"""
        today = datetime.now().date()
        return self.session.query(Order).filter(Order.timestamp >= today).all()
    
    def get_orders_not_sent(self):
        """Get orders not sent to report group"""
        return self.session.query(Order).filter_by(sent_to_group=False).all()
    
    def mark_order_sent(self, order_id):
        """Mark order as sent to report group"""
        order = self.session.query(Order).filter_by(id=order_id).first()
        if order:
            order.sent_to_group = True
            self.session.commit()
    
    def check_duplicate(self, phone, sku, days=30):
        """Check if order already exists (last 30 days)"""
        cutoff = datetime.now() - timedelta(days=days)
        return self.session.query(Order).filter(
            Order.phone == phone,
            Order.sku == sku,
            Order.timestamp >= cutoff
        ).order_by(Order.order_num.desc()).first()
    
    # ============ SKU ============
    def get_sku(self, sku_code):
        """Get SKU by code"""
        return self.session.query(SKU).filter_by(sku=sku_code, status='active').first()
    
    def get_all_skus(self):
        """Get all active SKUs"""
        return self.session.query(SKU).filter_by(status='active').all()
    
    def save_sku(self, sku_data):
        """Save or update SKU"""
        sku = self.get_sku(sku_data['sku'])
        if sku:
            sku.product_name = sku_data.get('product_name', sku.product_name)
            sku.price = sku_data.get('price', sku.price)
            sku.currency = sku_data.get('currency', 'BDT')
            sku.sizes = sku_data.get('sizes', sku.sizes)
            sku.image_url = sku_data.get('image_url', sku.image_url)
            sku.category = sku_data.get('category', sku.category)
            sku.brand = sku_data.get('brand', sku.brand)
        else:
            sku = SKU(
                sku=sku_data['sku'],
                product_name=sku_data.get('product_name', ''),
                price=sku_data.get('price', 0.0),
                currency=sku_data.get('currency', 'BDT'),
                sizes=sku_data.get('sizes', ''),
                image_url=sku_data.get('image_url', ''),
                category=sku_data.get('category', ''),
                brand=sku_data.get('brand', '')
            )
            self.session.add(sku)
        self.session.commit()
        return sku
    
    def delete_sku(self, sku_code):
        """Soft delete SKU (set inactive)"""
        sku = self.get_sku(sku_code)
        if sku:
            sku.status = 'inactive'
            self.session.commit()
            return True
        return False
    
    def update_sku_image(self, sku_code, image_url):
        """Update SKU image URL"""
        sku = self.get_sku(sku_code)
        if sku:
            sku.image_url = image_url
            self.session.commit()
            return True
        return False

# Singleton instance
db = DatabaseManager()
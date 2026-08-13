# steadfast-admin.py - Steadfast Admin Tool (With Recent Orders & Delete)

import requests
import json
import os
import time
from datetime import datetime
from database import db

# Your Steadfast Keys
API_KEY = "9jx7208qjhdp52kh2u26ee5nv8bdb4ow"
SECRET_KEY = "01itaayqvtwtj9ekox9elwcn"
BASE_URL = "https://portal.packzy.com/api/v1"

HEADERS = {
    "Api-Key": API_KEY,
    "Secret-Key": SECRET_KEY,
    "Content-Type": "application/json"
}

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    clear_screen()
    print("=" * 60)
    print("STEADFAST ADMIN TOOL")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def check_balance():
    """Check Steadfast balance"""
    print("\nChecking balance...")
    try:
        resp = requests.get(
            f"{BASE_URL}/get_balance",
            headers=HEADERS,
            timeout=10
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('status') == 200:
                print(f"\nCurrent Balance: {result.get('current_balance', 0)} BDT")
            else:
                print(f"Error: {result.get('message', 'Unknown error')}")
        else:
            print(f"HTTP Error: {resp.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

def get_all_orders():
    """Fetch all orders from Steadfast"""
    print("\nFetching all orders from Steadfast...")
    print("This may take a moment...")
    
    try:
        # Try to get orders from API
        resp = requests.get(
            f"{BASE_URL}/get_orders",
            headers=HEADERS,
            params={'limit': 100},
            timeout=15
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('status') == 200:
                orders = result.get('data', [])
                if orders:
                    return orders
                else:
                    print("No orders found in Steadfast.")
                    return []
            else:
                print(f"API Error: {result.get('message', 'Unknown')}")
                return []
        else:
            print(f"HTTP Error: {resp.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []

def get_orders_from_db():
    """Get orders from local database"""
    from database import db
    return db.get_today_orders()

def view_recent_orders():
    """View recent orders with delete option"""
    print("\n" + "=" * 60)
    print("RECENT ORDERS")
    print("=" * 60)
    
    # Get orders from local database first
    local_orders = get_orders_from_db()
    
    if local_orders:
        print(f"\nLocal Database Orders ({len(local_orders)}):")
        print("-" * 70)
        print(f"{'No.':<4} {'Order #':<8} {'Customer':<15} {'Phone':<15} {'SKU':<10} {'Price':<10} {'Status':<10}")
        print("-" * 70)
        
        for idx, order in enumerate(local_orders[:20], 1):
            status = "Shipped" if order.consignment_id else "Confirmed"
            print(f"{idx:<4} {order.order_num:<8} {order.customer_name[:15]:<15} {order.phone:<15} {order.sku:<10} {order.price:<10.2f} {status:<10}")
        
        print("-" * 70)
        total = sum(o.price for o in local_orders)
        print(f"Total: {len(local_orders)} orders | Amount: {total:.2f} BDT")
        print("=" * 60)
        
        # Ask if user wants to delete
        delete_choice = input("\nDelete an order? (yes/no): ").strip().lower()
        if delete_choice == 'yes':
            delete_order_from_db(local_orders)
    else:
        print("\nNo orders in local database.")
    
    # Try to get Steadfast orders
    print("\n" + "=" * 60)
    print("STEADFAST ORDERS")
    print("=" * 60)
    
    try:
        resp = requests.get(
            f"{BASE_URL}/get_orders",
            headers=HEADERS,
            params={'limit': 20},
            timeout=10
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('status') == 200:
                orders = result.get('data', [])
                if orders:
                    print(f"\nRecent Steadfast Orders ({len(orders)}):")
                    print("-" * 80)
                    print(f"{'No.':<4} {'Consignment ID':<15} {'Customer':<15} {'Phone':<15} {'Status':<12} {'COD':<8}")
                    print("-" * 80)
                    
                    for idx, order in enumerate(orders, 1):
                        consignment_id = order.get('consignment_id', 'N/A')
                        customer = order.get('recipient_name', 'Unknown')
                        phone = order.get('recipient_phone', 'N/A')
                        status = order.get('status', 'Unknown')
                        cod = order.get('cod_amount', 0)
                        print(f"{idx:<4} {str(consignment_id):<15} {customer[:15]:<15} {phone:<15} {status[:12]:<12} {cod:<8.2f}")
                    
                    print("-" * 80)
                    print("=" * 60)
                else:
                    print("No orders found in Steadfast.")
            else:
                print(f"API Error: {result.get('message', 'Unknown')}")
        else:
            print(f"HTTP Error: {resp.status_code}")
            
    except Exception as e:
        print(f"Error fetching Steadfast orders: {e}")

def delete_order_from_db(orders):
    """Delete an order from local database"""
    from database import db
    
    try:
        order_num = input("\nEnter Order Number to delete: ").strip()
        if not order_num:
            print("Order number required.")
            return
        
        confirm = input(f"Delete Order #{order_num}? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Deletion cancelled.")
            return
        
        # Find the order
        order_to_delete = None
        for order in orders:
            if str(order.order_num) == order_num:
                order_to_delete = order
                break
        
        if order_to_delete:
            # Delete from database
            db.session.delete(order_to_delete)
            db.session.commit()
            print(f"Order #{order_num} deleted successfully!")
        else:
            print(f"Order #{order_num} not found.")
            
    except Exception as e:
        print(f"Error deleting order: {e}")
        db.session.rollback()

def delete_steadfast_order():
    """Cancel/delete an order from Steadfast"""
    print("\n" + "=" * 60)
    print("CANCEL STEADFAST ORDER")
    print("=" * 60)
    
    consignment_id = input("\nEnter Consignment ID to cancel: ").strip()
    if not consignment_id:
        print("Consignment ID required.")
        return
    
    confirm = input(f"Cancel order {consignment_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    try:
        resp = requests.post(
            f"{BASE_URL}/cancel_order/{consignment_id}",
            headers=HEADERS,
            timeout=10
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('status') == 200:
                print(f"Order {consignment_id} cancelled successfully!")
            else:
                print(f"Error: {result.get('message', 'Unknown error')}")
        else:
            print(f"HTTP Error: {resp.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

def get_order_by_invoice():
    """Get order by invoice"""
    invoice = input("\nEnter Invoice Number: ").strip()
    if not invoice:
        print("Invoice number required.")
        return
    
    print(f"\nSearching for invoice: {invoice}")
    try:
        resp = requests.get(
            f"{BASE_URL}/status_by_invoice/{invoice}",
            headers=HEADERS,
            timeout=10
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('status') == 200:
                print(f"\nDelivery Status: {result.get('delivery_status', 'Unknown')}")
            else:
                print(f"Error: {result.get('message', 'Order not found')}")
        else:
            print(f"HTTP Error: {resp.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

def get_order_by_consignment():
    """Get order by consignment ID"""
    consignment_id = input("\nEnter Consignment ID: ").strip()
    if not consignment_id:
        print("Consignment ID required.")
        return
    
    print(f"\nSearching for consignment: {consignment_id}")
    try:
        resp = requests.get(
            f"{BASE_URL}/status_by_cid/{consignment_id}",
            headers=HEADERS,
            timeout=10
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('status') == 200:
                print(f"\nDelivery Status: {result.get('delivery_status', 'Unknown')}")
            else:
                print(f"Error: {result.get('message', 'Order not found')}")
        else:
            print(f"HTTP Error: {resp.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

def get_label_url():
    """Generate label URL"""
    consignment_id = input("\nEnter Consignment ID: ").strip()
    if not consignment_id:
        print("Consignment ID required.")
        return
    
    size = input("Label Size (2x3, 4x6, A4): ").strip() or "2x3"
    url = f"https://www.steadfast.com.bd/user/consignment/print-label/{consignment_id}?size={size}"
    
    print("\nLabel URL:")
    print("=" * 60)
    print(url)
    print("=" * 60)

def view_local_orders():
    """View all orders from local database only"""
    from database import db
    
    orders = db.get_today_orders()
    if not orders:
        print("No orders in database.")
        return
    
    print(f"\nOrders in Database ({len(orders)}):")
    print("-" * 70)
    print(f"{'Order #':<8} {'Customer':<15} {'Phone':<15} {'SKU':<10} {'Price':<10} {'Status':<10}")
    print("-" * 70)
    
    for order in orders:
        status = "Shipped" if order.consignment_id else "Confirmed"
        print(f"{order.order_num:<8} {order.customer_name[:15]:<15} {order.phone:<15} {order.sku:<10} {order.price:<10.2f} {status:<10}")
    
    print("-" * 70)
    total = sum(o.price for o in orders)
    print(f"Total Orders: {len(orders)} | Total Amount: {total:.2f} BDT")

def test_connection():
    """Test Steadfast API connection"""
    print("\nTesting Steadfast API connection...")
    try:
        resp = requests.get(
            f"{BASE_URL}/get_balance",
            headers=HEADERS,
            timeout=5
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('status') == 200:
                print("Connection: SUCCESS")
                print(f"Balance: {result.get('current_balance', 0)} BDT")
                return True
            else:
                print(f"Connection: FAILED - {result.get('message', 'Unknown')}")
                return False
        else:
            print(f"Connection: FAILED - HTTP {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"Connection: FAILED - {e}")
        return False

def show_menu():
    print_header()
    
    # Show connection status
    print("\nCONNECTION STATUS")
    print("-" * 40)
    try:
        resp = requests.get(
            f"{BASE_URL}/get_balance",
            headers=HEADERS,
            timeout=3
        )
        if resp.status_code == 200:
            print("Status: CONNECTED")
        else:
            print(f"Status: ERROR ({resp.status_code})")
    except:
        print("Status: OFFLINE")
    print("-" * 40)
    
    print("\nMAIN MENU")
    print("-" * 50)
    print("1. View Recent Orders (with Delete)")
    print("2. Check Balance")
    print("3. Cancel Steadfast Order")
    print("4. Search by Invoice")
    print("5. Search by Consignment ID")
    print("6. Generate Label URL")
    print("7. View Local Orders")
    print("8. Test Connection")
    print("0. Exit")
    print("-" * 50)
    
    choice = input("Select Option: ").strip()
    
    if choice == '1':
        view_recent_orders()
    elif choice == '2':
        check_balance()
    elif choice == '3':
        delete_steadfast_order()
    elif choice == '4':
        get_order_by_invoice()
    elif choice == '5':
        get_order_by_consignment()
    elif choice == '6':
        get_label_url()
    elif choice == '7':
        view_local_orders()
    elif choice == '8':
        test_connection()
    elif choice == '0':
        print("Exiting...")
        return False
    else:
        print("Invalid option.")
    
    print("\nPress Enter to continue...")
    input()
    return True

def main():
    print("=" * 60)
    print("STEADFAST ADMIN TOOL")
    print("=" * 60)
    print("Loading...")
    time.sleep(1)
    
    running = True
    while running:
        running = show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from auth import (AdminAuth, ProductManager, OrderManager, UserManager, 
                 FAQManager, UnansweredQuestionManager, RoleManager)

def test_basic_functionality():
    """Simple tests to verify basic functionality"""
    
    # Test AdminAuth
    print("=== Testing AdminAuth ===")
    auth = AdminAuth()
    
    # Test password hashing
    password = "test123"
    hashed = auth.hash_password(password)
    print(f"Password hashing works: {len(hashed) == 64}")  # SHA-256 produces 64 chars
    
    # Test admin login (using credentials from setup.py)
    user_info = auth.verify_admin_user("product_admin", "admin123")
    print(f"Product admin login: {user_info is not None}")
    if user_info:
        print(f"User info: {user_info}")
    
    # Test access control
    print(f"Product admin can access products: {auth.check_access('Product Admin', 'products')}")
    print(f"Product admin can access orders: {auth.check_access('Product Admin', 'orders')}")
    print(f"Product admin cannot access roles: {auth.check_access('Product Admin', 'roles')}")
    
    # Test ProductManager
    print("\n=== Testing ProductManager ===")
    product_manager = ProductManager()
    
    products = product_manager.get_all()
    print(f"Retrieved {len(products)} products")
    if products:
        print(f"First product: {products[0]}")
    
    # Test creating a product
    result = product_manager.create("Test Product", 10, 1, "pcs")
    print(f"Create product result: {result}")
    
    # Test OrderManager
    print("\n=== Testing OrderManager ===")
    order_manager = OrderManager()
    
    orders = order_manager.get_all()
    print(f"Retrieved {len(orders)} orders")
    if orders:
        print(f"First order: {orders[0]}")
    
    # Test UserManager
    print("\n=== Testing UserManager ===")
    user_manager = UserManager()
    
    users = user_manager.get_all()
    print(f"Retrieved {len(users)} users")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_basic_functionality()


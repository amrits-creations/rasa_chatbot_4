from auth import *

def test_full_workflow():
    """Test complete admin workflow"""
    
    print("=== Full Integration Test ===")
    
    # 1. Test authentication
    auth = AdminAuth()
    user_info = auth.verify_admin_user("app_admin", "admin123")
    
    if not user_info:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authenticated as: {user_info['username']} ({user_info['role']})")
    
    # 2. Test CRUD operations based on role
    user_role = user_info['role']
    
    if auth.check_access(user_role, 'products'):
        print("\n--- Testing Product Operations ---")
        product_manager = ProductManager()
        
        # Create
        result = product_manager.create("Integration Test Product", 5, 1, "pcs")
        print(f"Create: {result['message']}")
        
        # Read
        products = product_manager.get_all()
        test_product = None
        for p in products:
            if p['product_name'] == "Integration Test Product":
                test_product = p
                break
        
        if test_product:
            print(f"Read: Found product {test_product['product_id']}")
            
            # Update
            result = product_manager.update(
                test_product['product_id'], 
                "Updated Test Product", 
                10, 
                2, 
                "pcs"
            )
            print(f"Update: {result['message']}")
            
            # Delete
            result = product_manager.delete(test_product['product_id'])
            print(f"Delete: {result['message']}")
    
    if auth.check_access(user_role, 'orders'):
        print("\n--- Testing Order Operations ---")
        order_manager = OrderManager()
        
        orders = order_manager.get_all()
        print(f"Found {len(orders)} orders")
        
        if orders:
            # Test updating first order
            first_order = orders[0]
            result = order_manager.update(
                first_order['order_id'], 
                "Updated Status", 
                "2025-12-31"
            )
            print(f"Order update: {result['message']}")

if __name__ == "__main__":
    test_full_workflow()


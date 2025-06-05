import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from auth import (AdminAuth, ProductManager, OrderManager, UserManager, 
                 FAQManager, UnansweredQuestionManager, RoleManager)

class TestAdminAuth(unittest.TestCase):
    """Test AdminAuth class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.auth = AdminAuth()
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        password = "test123"
        hashed = self.auth.hash_password(password)
        
        # SHA-256 hash should be 64 characters long
        self.assertEqual(len(hashed), 64)
        
        # Same password should produce same hash
        hashed2 = self.auth.hash_password(password)
        self.assertEqual(hashed, hashed2)
        
        # Different passwords should produce different hashes
        different_hash = self.auth.hash_password("different123")
        self.assertNotEqual(hashed, different_hash)
    
    def test_valid_admin_login(self):
        """Test valid admin user login"""
        # Using credentials from setup.py
        user_info = self.auth.verify_admin_user("product_admin", "admin123")
        
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], 'product_admin')
        self.assertEqual(user_info['role'], 'Product Admin')
    
    def test_invalid_login(self):
        """Test invalid login attempts"""
        # Wrong password
        result = self.auth.verify_admin_user("product_admin", "wrong_password")
        self.assertIsNone(result)
        
        # Non-existent user
        result = self.auth.verify_admin_user("fake_user", "admin123")
        self.assertIsNone(result)
    
    def test_access_control(self):
        """Test role-based access control"""
        # Product Admin access
        self.assertTrue(self.auth.check_access('Product Admin', 'products'))
        self.assertTrue(self.auth.check_access('Product Admin', 'orders'))
        self.assertFalse(self.auth.check_access('Product Admin', 'roles'))
        
        # Order Admin access
        self.assertTrue(self.auth.check_access('Order Admin', 'orders'))
        self.assertFalse(self.auth.check_access('Order Admin', 'products'))
        
        # System Admin access
        self.assertTrue(self.auth.check_access('System Admin', 'roles'))
        self.assertTrue(self.auth.check_access('System Admin', 'products'))

class TestProductManager(unittest.TestCase):
    """Test ProductManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.product_manager = ProductManager()
    
    def test_get_all_products(self):
        """Test retrieving all products"""
        products = self.product_manager.get_all()
        self.assertIsInstance(products, list)
        
        if products:  # If products exist
            product = products[0]
            self.assertIn('product_id', product)
            self.assertIn('product_name', product)
            self.assertIn('current_stock', product)

class TestOrderManager(unittest.TestCase):
    """Test OrderManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.order_manager = OrderManager()
    
    def test_get_all_orders(self):
        """Test retrieving all orders"""
        orders = self.order_manager.get_all()
        self.assertIsInstance(orders, list)
        
        if orders:  # If orders exist
            order = orders[0]
            self.assertIn('order_id', order)
            self.assertIn('username', order)
            self.assertIn('status', order)

if __name__ == '__main__':
    unittest.main(verbosity=2)


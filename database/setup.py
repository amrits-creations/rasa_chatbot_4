import hashlib
from models import Base, Role, User, Product, Order, FAQ, create_engine_instance, create_session
from datetime import date

def setup_database():
    """Complete database setup including tables, sample data, and admin users"""
    print("Setting up database...")

    # Create all tables
    engine = create_engine_instance()
    Base.metadata.create_all(engine)
    print("✅ Tables created successfully!")

    session = create_session()

    try:
        # Add roles
        roles_data = [
            'System Admin',
            'Application Admin',
            'Product Admin',
            'Order Admin',
            'End User'
        ]

        for role_name in roles_data:
            if not session.query(Role).filter_by(role_name=role_name).first():
                role = Role(role_name=role_name)
                session.add(role)

        session.commit()
        print("✅ Roles added successfully!")

        # Create admin users for Application Admin, Product Admin, and Order Admin
        admin_users_data = [
            ('app_admin', 'admin123', 'Application Admin'),
            ('product_admin', 'admin123', 'Product Admin'),
            ('order_admin', 'admin123', 'Order Admin')
        ]

        for username, password, role_name in admin_users_data:
            # Get the role
            admin_role = session.query(Role).filter_by(role_name=role_name).first()
            
            if admin_role:
                # Check if admin user already exists
                existing_admin = session.query(User).filter_by(username=username).first()
                
                if not existing_admin:
                    # Hash password
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    admin_user = User(
                        username=username,
                        password=password_hash,
                        role_id=admin_role.role_id
                    )
                    session.add(admin_user)
                    print(f"✅ {role_name} user '{username}' created successfully!")
                else:
                    print(f"ℹ️  {role_name} user '{username}' already exists")

        # Add sample end user
        user_role = session.query(Role).filter_by(role_name='End User').first()
        if not session.query(User).filter_by(username='testuser').first():
            # Hash password for test user
            test_password_hash = hashlib.sha256('test123'.encode()).hexdigest()
            test_user = User(
                username='testuser',
                password=test_password_hash,
                role_id=user_role.role_id
            )
            session.add(test_user)

        session.commit()
        print("✅ Users added successfully!")

        # Add products
        products_data = [
            ('Jacket', 50, 1, 'pcs'),
            ('Shoes', 30, 1, 'pcs'),
            ('Headphones', 25, 1, 'pcs'),
            ('Laptop 2000', 10, 1, 'pcs'),
            ('Smartphone 500', 20, 1, 'pcs')
        ]

        for name, stock, moq, qty_type in products_data:
            if not session.query(Product).filter_by(product_name=name).first():
                product = Product(
                    product_name=name,
                    current_stock=stock,
                    moq=moq,
                    quantity_type=qty_type
                )
                session.add(product)

        session.commit()
        print("✅ Products added successfully!")

        # Add sample orders
        test_user_obj = session.query(User).filter_by(username='testuser').first()
        jacket = session.query(Product).filter_by(product_name='Jacket').first()
        shoes = session.query(Product).filter_by(product_name='Shoes').first()
        headphones = session.query(Product).filter_by(product_name='Headphones').first()

        if jacket and shoes and headphones and test_user_obj:
            orders_data = [
                (12345, jacket.product_id, 'Shipped', date(2025, 6, 10)),
                (98765, headphones.product_id, 'Processing', date(2025, 6, 12)),
                (12346, shoes.product_id, 'Shipped', date(2025, 6, 10))
            ]

            for order_id, product_id, status, delivery_date in orders_data:
                if not session.query(Order).filter_by(order_id=order_id).first():
                    order = Order(
                        order_id=order_id,
                        user_id=test_user_obj.user_id,
                        product_id=product_id,
                        status=status,
                        estimated_delivery=delivery_date
                    )
                    session.add(order)

        session.commit()
        print("✅ Orders added successfully!")

        # Add FAQs
        faqs_data = [
            ("What are your store hours?", "Our store is open 9 AM–9 PM Monday through Saturday, and 10 AM–6 PM on Sundays."),
            ("What is your return policy?", "You can return any item within 30 days for a full refund. Just visit our Returns page."),
            ("How can I contact support?", "You can reach us at support@example.com or call 1-800-123-4567.")
        ]

        for question, answer in faqs_data:
            if not session.query(FAQ).filter_by(question=question).first():
                faq = FAQ(question=question, answer=answer)
                session.add(faq)

        session.commit()
        print("✅ FAQs added successfully!")
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📋 Admin Credentials Created:")
        print("Application Admin - Username: app_admin, Password: admin123")
        print("Product Admin - Username: product_admin, Password: admin123") 
        print("Order Admin - Username: order_admin, Password: admin123")

    except Exception as e:
        session.rollback()
        print(f"❌ Error setting up database: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    setup_database()

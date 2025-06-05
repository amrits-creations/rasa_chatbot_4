import hashlib
import sys
import os

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

try:
    from models import create_session, User, Role, Product, Order, FAQ, UnansweredQuestion
except ImportError:
    create_session = None
    User = None
    Role = None
    Product = None
    Order = None
    FAQ = None
    UnansweredQuestion = None

class AdminAuth:
    """Simple authentication for admin users"""

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_admin_user(self, username, password):
        """Check if user credentials are valid"""
        if not create_session or not User or not Role:
            return None

        session = create_session()
        try:
            user = session.query(User).join(Role).filter(
                User.username == username
            ).first()

            if not user:
                return None

            hashed_input = self.hash_password(password)
            if user.password != hashed_input:
                return None

            # Check if user has admin privileges
            admin_roles = ['System Admin', 'Application Admin', 'Product Admin', 'Order Admin']
            if user.role.role_name not in admin_roles:
                return None

            return {
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role.role_name
            }

        except Exception as e:
            print(f"Auth error: {e}")
            return None
        finally:
            session.close()

    def check_access(self, user_role, resource):
        """Check if user role has access to resource"""
        if user_role == 'System Admin':
            return resource in ['roles', 'users', 'products', 'orders', 'faq', 'unanswered']
        elif user_role == 'Application Admin':
            return resource in ['users', 'products', 'orders', 'faq', 'unanswered']
        elif user_role == 'Product Admin':
            return resource in ['products', 'orders']
        elif user_role == 'Order Admin':
            return resource in ['orders']
        else:
            return False

class ProductManager:
    """Product CRUD operations"""
    
    def get_all(self):
        if not create_session or not Product:
            return []
        
        session = create_session()
        try:
            products = session.query(Product).all()
            product_list = []
            for p in products:
                product_dict = {
                    'product_id': p.product_id,
                    'product_name': p.product_name,
                    'current_stock': p.current_stock,
                    'moq': p.moq,
                    'quantity_type': p.quantity_type
                }
                product_list.append(product_dict)
            return product_list
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            session.close()

    def create(self, name, stock, moq, qty_type):
        if not create_session or not Product:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            product = Product(
                product_name=name,
                current_stock=stock,
                moq=moq,
                quantity_type=qty_type
            )
            session.add(product)
            session.commit()
            return {'success': True, 'message': f'Product "{name}" created'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def update(self, product_id, name, stock, moq, qty_type):
        if not create_session or not Product:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            product = session.query(Product).filter_by(product_id=product_id).first()
            if not product:
                return {'success': False, 'message': 'Product not found'}

            if name:
                product.product_name = name
            if stock is not None:
                product.current_stock = stock
            if moq is not None:
                product.moq = moq
            if qty_type:
                product.quantity_type = qty_type
            
            session.commit()
            return {'success': True, 'message': 'Product updated successfully'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def delete(self, product_id):
        if not create_session or not Product:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            product = session.query(Product).filter_by(product_id=product_id).first()
            if not product:
                return {'success': False, 'message': 'Product not found'}

            name = product.product_name
            session.delete(product)
            session.commit()
            return {'success': True, 'message': f'Product "{name}" deleted'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

class OrderManager:
    """Order CRUD operations"""
    
    def get_all(self):
        if not create_session or not Order:
            return []
        
        session = create_session()
        try:
            orders = session.query(Order).join(Product).join(User).all()
            order_list = []
            for o in orders:
                order_dict = {
                    'order_id': o.order_id,
                    'username': o.user.username,
                    'product_name': o.product.product_name,
                    'status': o.status,
                    'estimated_delivery': str(o.estimated_delivery) if o.estimated_delivery else None
                }
                order_list.append(order_dict)
            return order_list
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            session.close()

    def create(self, user_id, product_id, status, estimated_delivery):
        if not create_session or not Order:
            return {'success': False, 'message': 'Database not available'}
    
        session = create_session()
        try:
            # Check if user exists
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return {'success': False, 'message': 'User not found'}
    
            # Check if product exists
            product = session.query(Product).filter_by(product_id=product_id).first()
            if not product:
                return {'success': False, 'message': 'Product not found'}
    
            # Create new order
            order = Order(
                user_id=user_id,
                product_id=product_id,
                status=status if status else 'pending',
                estimated_delivery=estimated_delivery
            )
            session.add(order)
            session.commit()
    
            return {
                'success': True, 
                'message': f'Order created successfully for user {user.username} - Product: {product.product_name}',
                'order_id': order.order_id
            }
    
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error creating order: {str(e)}'}
        finally:
            session.close()


    def update(self, order_id, status, estimated_delivery):
        if not create_session or not Order:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            order = session.query(Order).filter_by(order_id=order_id).first()
            if not order:
                return {'success': False, 'message': 'Order not found'}

            if status:
                order.status = status
            if estimated_delivery:
                order.estimated_delivery = estimated_delivery
            
            session.commit()
            return {'success': True, 'message': 'Order updated successfully'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def delete(self, order_id):
        if not create_session or not Order:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            order = session.query(Order).filter_by(order_id=order_id).first()
            if not order:
                return {'success': False, 'message': 'Order not found'}

            session.delete(order)
            session.commit()
            return {'success': True, 'message': f'Order {order_id} deleted'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

class UserManager:
    """User CRUD operations"""
    
    def get_all(self):
        if not create_session or not User:
            return []
        
        session = create_session()
        try:
            users = session.query(User).join(Role).all()
            user_list = []
            for u in users:
                user_dict = {
                    'user_id': u.user_id,
                    'username': u.username,
                    'role_name': u.role.role_name
                }
                user_list.append(user_dict)
            return user_list
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            session.close()

    def create(self, username, password, role_name):
        if not create_session or not User or not Role:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            role = session.query(Role).filter_by(role_name=role_name).first()
            if not role:
                return {'success': False, 'message': 'Role not found'}

            auth = AdminAuth()
            hashed_password = auth.hash_password(password)
            user = User(
                username=username,
                password=hashed_password,
                role_id=role.role_id
            )
            session.add(user)
            session.commit()
            return {'success': True, 'message': f'User "{username}" created'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def update(self, user_id, username, password, role_name):
        if not create_session or not User or not Role:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return {'success': False, 'message': 'User not found'}
    
            # Update username if provided
            if username:
                # Check if new username already exists (exclude current user)
                existing_user = session.query(User).filter(
                    User.username == username,
                    User.user_id != user_id
                ).first()
                if existing_user:
                    return {'success': False, 'message': 'Username already exists'}
                user.username = username

            # Update password if provided
            if password:
                auth = AdminAuth()
                user.password = auth.hash_password(password)

            # Update role if provided
            if role_name:
                role = session.query(Role).filter_by(role_name=role_name).first()
                if not role:
                    return {'success': False, 'message': 'Role not found'}
                user.role_id = role.role_id

            session.commit()
            return {'success': True, 'message': f'User "{user.username}" updated successfully'}

        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()


    def delete(self, user_id):
        if not create_session or not User:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return {'success': False, 'message': 'User not found'}

            username = user.username
            session.delete(user)
            session.commit()
            return {'success': True, 'message': f'User "{username}" deleted'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

class FAQManager:
    """FAQ CRUD operations"""
    
    def get_all(self):
        if not create_session or not FAQ:
            return []
        
        session = create_session()
        try:
            faqs = session.query(FAQ).all()
            faq_list = []
            for f in faqs:
                faq_dict = {
                    'faq_id': f.faq_id,
                    'question': f.question,
                    'answer': f.answer
                }
                faq_list.append(faq_dict)
            return faq_list
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            session.close()

    def create(self, question, answer):
        if not create_session or not FAQ:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            faq = FAQ(question=question, answer=answer)
            session.add(faq)
            session.commit()
            return {'success': True, 'message': 'FAQ created successfully'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def update(self, faq_id, question, answer):
        if not create_session or not FAQ:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            faq = session.query(FAQ).filter_by(faq_id=faq_id).first()
            if not faq:
                return {'success': False, 'message': 'FAQ not found'}

            if question:
                faq.question = question
            if answer:
                faq.answer = answer
            
            session.commit()
            return {'success': True, 'message': 'FAQ updated successfully'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def delete(self, faq_id):
        if not create_session or not FAQ:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            faq = session.query(FAQ).filter_by(faq_id=faq_id).first()
            if not faq:
                return {'success': False, 'message': 'FAQ not found'}

            session.delete(faq)
            session.commit()
            return {'success': True, 'message': 'FAQ deleted successfully'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

class UnansweredQuestionManager:
    """Unanswered Questions CRUD operations"""
    
    def get_all(self):
        if not create_session or not UnansweredQuestion:
            return []
        
        session = create_session()
        try:
            questions = session.query(UnansweredQuestion).all()
            question_list = []
            for q in questions:
                question_dict = {
                    'uq_id': q.uq_id,
                    'question': q.question,
                    'status': q.status
                }
                question_list.append(question_dict)
            return question_list
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            session.close()

    def update(self, uq_id, status):
        if not create_session or not UnansweredQuestion:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            question = session.query(UnansweredQuestion).filter_by(uq_id=uq_id).first()
            if not question:
                return {'success': False, 'message': 'Question not found'}

            if status:
                question.status = status
            
            session.commit()
            return {'success': True, 'message': 'Question updated successfully'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def delete(self, uq_id):
        if not create_session or not UnansweredQuestion:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            question = session.query(UnansweredQuestion).filter_by(uq_id=uq_id).first()
            if not question:
                return {'success': False, 'message': 'Question not found'}

            session.delete(question)
            session.commit()
            return {'success': True, 'message': 'Question deleted successfully'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

class RoleManager:
    """Role CRUD operations (System Admin only)"""
    
    def get_all(self):
        if not create_session or not Role:
            return []
        
        session = create_session()
        try:
            roles = session.query(Role).all()
            role_list = []
            for r in roles:
                role_dict = {
                    'role_id': r.role_id,
                    'role_name': r.role_name
                }
                role_list.append(role_dict)
            return role_list
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            session.close()

    def create(self, role_name):
        if not create_session or not Role:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            role = Role(role_name=role_name)
            session.add(role)
            session.commit()
            return {'success': True, 'message': f'Role "{role_name}" created'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

    def delete(self, role_id):
        if not create_session or not Role:
            return {'success': False, 'message': 'Database not available'}

        session = create_session()
        try:
            role = session.query(Role).filter_by(role_id=role_id).first()
            if not role:
                return {'success': False, 'message': 'Role not found'}

            role_name = role.role_name
            session.delete(role)
            session.commit()
            return {'success': True, 'message': f'Role "{role_name}" deleted'}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}
        finally:
            session.close()

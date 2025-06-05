from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sys
import os

# Add the database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

try:
    from models import create_session, UnansweredQuestion, Product, Order
except ImportError:
    # Fallback if database not available
    create_session = None
    UnansweredQuestion = None
    Product = None
    Order = None

class ActionFetchOrderStatus(Action):
    """Look up order status from database"""

    def name(self) -> Text:
        return "action_fetch_order_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_number = tracker.get_slot("ordernumber")
        
        if not order_number:
            dispatcher.utter_message(text="I need an order number to look up your status.")
            return []

        if not Order or not create_session:
            dispatcher.utter_message(text="Sorry, order database is not available.")
            return []

        session = create_session()
        try:
            order_id = int(order_number)
            order = session.query(Order).filter_by(order_id=order_id).first()

            if order:
                message = (f"Order {order_number} is {order.status}. "
                          f"Items: {order.product.product_name}. "
                          f"Estimated delivery: {order.estimated_delivery}.")
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text=f"Sorry, order {order_number} was not found.")

        except ValueError:
            dispatcher.utter_message(text="Please provide a valid order number.")
        except Exception as e:
            dispatcher.utter_message(text="Sorry, I'm having trouble accessing the order database.")
            print(f"Database error: {e}")
        finally:
            session.close()

        return []

class ActionLogUnknownQuestion(Action):
    """Save unknown questions to database for review"""

    def name(self) -> Text:
        return "action_log_unknown_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text', '')

        # Save question to database if available
        if create_session and UnansweredQuestion:
            session = create_session()
            try:
                question = UnansweredQuestion(question=user_message)
                session.add(question)
                session.commit()
                print(f"Saved unknown question: {user_message}")
            except Exception as e:
                print(f"Database error: {e}")
            finally:
                session.close()

        # Show helpful message to user
        help_message = ("I'm sorry, I didn't understand that. I can help you with:\n"
                       "• Order status (just give me your order number)\n"
                       "• Store hours\n"
                       "• Return policy\n"
                       "• Contact information\n"
                       "• Product information\n"
                       "Or you can reach support at support@example.com")
        
        dispatcher.utter_message(text=help_message)
        return []

class ActionGetProductInfo(Action):
    """Find product information using simple text matching"""

    def name(self) -> Text:
        return "action_get_product_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("productname")

        if not product_name:
            dispatcher.utter_message(text="Which product would you like to know about?")
            return []

        if not Product or not create_session:
            dispatcher.utter_message(text="Sorry, product database is not available.")
            return []

        session = create_session()
        try:
            # Get all products from database
            all_products = session.query(Product).all()
            
            # Find exact match first (case insensitive)
            exact_match = None
            for product in all_products:
                if product.product_name.lower() == product_name.lower():
                    exact_match = product
                    break

            if exact_match:
                self.send_product_info(dispatcher, exact_match)
            else:
                # Look for partial matches (case insensitive)
                partial_matches = []
                for product in all_products:
                    if product_name.lower() in product.product_name.lower():
                        partial_matches.append(product)

                if len(partial_matches) == 1:
                    # Found one partial match
                    self.send_product_info(dispatcher, partial_matches[0])
                elif len(partial_matches) > 1:
                    # Found multiple partial matches
                    product_names = [p.product_name for p in partial_matches]
                    dispatcher.utter_message(text=f"I found multiple products matching '{product_name}': {', '.join(product_names)}. Which one would you like to know about?.")
                else:
                    # No matches found
                    all_product_names = [p.product_name for p in all_products]
                    dispatcher.utter_message(text=f"Sorry, I couldn't find '{product_name}'. Available products: {', '.join(all_product_names)}")

        except Exception as e:
            dispatcher.utter_message(text="Sorry, I'm having trouble accessing the product database.")
            print(f"Product database error: {e}")
        finally:
            session.close()

        return []

    def send_product_info(self, dispatcher: CollectingDispatcher, product: Product):
        """Send product information to user"""
        # Check stock status
        if product.current_stock > 0:
            if product.current_stock <= 5:
                stock_status = "✅ In Stock (Low Stock!)"
            else:
                stock_status = "✅ In Stock"
        else:
            stock_status = "❌ Out of Stock"

        # Create message
        message = (f"📦 **{product.product_name}**\n"
                  f"📊 Stock: {product.current_stock} {product.quantity_type}\n"
                  f"📦 Minimum Order: {product.moq} {product.quantity_type}\n"
                  f"🏷️ Status: {stock_status}")
        
        dispatcher.utter_message(text=message)

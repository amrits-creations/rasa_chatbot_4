from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': os.getenv('DB_SCHEMA', 'chatbot_v4')}

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), nullable=False, unique=True)

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': os.getenv('DB_SCHEMA', 'chatbot_v4')}

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey(f"{os.getenv('DB_SCHEMA', 'chatbot_v4')}.roles.role_id"), nullable=False)

    role = relationship("Role", back_populates="users")
    orders = relationship("Order", back_populates="user")

class Product(Base):
    __tablename__ = 'products'
    __table_args__ = {'schema': os.getenv('DB_SCHEMA', 'chatbot_v4')}

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    moq = Column(Integer, nullable=False, default=1)
    quantity_type = Column(String(20), nullable=False)

    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = {'schema': os.getenv('DB_SCHEMA', 'chatbot_v4')}

    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f"{os.getenv('DB_SCHEMA', 'chatbot_v4')}.users.user_id"), nullable=False)
    product_id = Column(Integer, ForeignKey(f"{os.getenv('DB_SCHEMA', 'chatbot_v4')}.products.product_id"), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    estimated_delivery = Column(Date)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

class FAQ(Base):
    __tablename__ = 'faq'
    __table_args__ = {'schema': os.getenv('DB_SCHEMA', 'chatbot_v4')}

    faq_id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

class UnansweredQuestion(Base):
    __tablename__ = 'unanswered_questions'
    __table_args__ = {'schema': os.getenv('DB_SCHEMA', 'chatbot_v4')}

    uq_id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='new')

def get_database_url():
    return f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def create_engine_instance():
    return create_engine(get_database_url())

def create_session():
    engine = create_engine_instance()
    Session = sessionmaker(bind=engine)
    return Session()

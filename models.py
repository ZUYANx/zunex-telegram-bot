from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_FILE

Base = declarative_base()

class Setting(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_num = Column(Integer, nullable=False)
    customer_name = Column(String(100), default='Unknown')
    phone = Column(String(15), nullable=False)
    address = Column(Text, nullable=False)
    sku = Column(String(50), default='N/A')
    product_name = Column(String(200), default='')
    quantity = Column(Integer, default=1)
    size = Column(String(50), default='')
    price = Column(Float, default=0.0)
    status = Column(String(20), default='confirmed')
    timestamp = Column(DateTime, default=datetime.now)
    consignment_id = Column(String(50), default='')
    sent_to_group = Column(Boolean, default=False)

class SKU(Base):
    __tablename__ = 'skus'
    
    sku = Column(String(50), primary_key=True)
    product_name = Column(String(200), nullable=False)
    price = Column(Float, default=0.0)
    currency = Column(String(10), default='BDT')
    sizes = Column(String(200), default='')  # Comma separated: 36,38,40,42
    image_url = Column(String(500), default='')
    category = Column(String(100), default='')
    brand = Column(String(100), default='')
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.now)

# Create engine
engine = create_engine(f'sqlite:///{DATABASE_FILE}', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
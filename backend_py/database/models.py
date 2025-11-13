from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)  # buy/sell
    amount = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # open/closed/cancelled
    profit_loss = Column(Float, nullable=True)
    strategy = Column(String)

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)  # long/short
    amount = Column(Float)
    entry_price = Column(Float)
    current_price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # open/closed
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)

class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
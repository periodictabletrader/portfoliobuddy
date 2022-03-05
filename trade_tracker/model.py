from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from .constants import DB_NAME
from .configs import DEFAULT_CCY

# TODO - Check if it's okay to use check_same_thread
engine = create_engine('sqlite:///{}?check_same_thread=False'.format(DB_NAME), pool_pre_ping=True)
Base = declarative_base(bind=engine)
Session = scoped_session(sessionmaker(bind=engine, autoflush=False))


def session():
    s = sessionmaker(bind=engine)
    return s()


class Trade(Base):
    __tablename__ = 'trades'
    tradeid = Column(Integer, primary_key=True)
    tradedate = Column(Date, nullable=False)
    ticker = Column(String, nullable=False)
    idea = Column(String)
    account = Column(String, ForeignKey('account.account'), nullable=False)
    ccy = Column(String, nullable=False, default=DEFAULT_CCY)
    qty = Column(Float, nullable=False)
    buy_cost = Column(Float, nullable=False, default=0)

    def __str__(self):
        return f'''
        Trade ({self.tradeid}, {self.tradedate}, {self.ticker}, {self.idea}, {self.account}, {self.ccy}, {self.qty},
               {self.buy_cost})
        '''.strip()


class ClosedTrade(Base):
    __tablename__ = 'closed_trades'
    tradeid = Column(Integer, primary_key=True)
    buydate = Column(Date, nullable=False)
    selldate = Column(Date, nullable=False)
    ticker = Column(String, nullable=False)
    idea = Column(String)
    account = Column(String, ForeignKey('account.account'))
    ccy = Column(String, nullable=False, default=DEFAULT_CCY)
    buy_cost = Column(Float, nullable=False, default=0)
    sell_value = Column(Float)

    def __str__(self):
        return f'''
        Trade ({self.tradeid}, {self.buydate}, {self.selldate}, {self.ticker}, {self.idea}, {self.account}, {self.ccy},
               {self.buy_cost}, {self.sell_value})
        '''.strip()


class PriceOverride(Base):
    __tablename__ = 'px_override'
    override_id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    px = Column(Float, nullable=False)


class Account(Base):
    __tablename__ = 'account'
    account = Column(String, nullable=False, primary_key=True)
    is_liquid = Column(Boolean, nullable=False)


class User(Base):
    __tablename__ = 'users'
    userid = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)

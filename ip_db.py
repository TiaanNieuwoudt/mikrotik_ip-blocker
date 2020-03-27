from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os


dir_path = os.getcwd()
engine = create_engine('sqlite:////home/pi/ip_db.db')

Base = declarative_base()

Session = sessionmaker()
Session.configure(bind=engine)
Session = scoped_session(Session)


class IPs(Base):
    __tablename__ = 'ips'
    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    date_time = Column(String)


    @classmethod
    def insert_IP(cls, ip_address, date_time):
        date_time = date_time.strftime("%d-%m-%y %H:%M:%S")
        validate_query = cls.query_ip(ip_address)
        if not validate_query:
            row = cls(ip_address=ip_address, date_time=date_time)
            session = Session()
            session.add(row)
            session.commit()
        else:
            print("IP already exists")

    @classmethod
    def query_ip(cls, ip_address):
        session = Session()
        query = session.query(cls.ip_address).filter(cls.ip_address == ip_address).all()
        print(query)
        return query

    @classmethod
    def query_date(cls):
        session = Session()
        query = session.query(cls.ip_address, cls.date_time).all()
        print(query)
        return query

    def save_to_db(self):
        session = Session()
        session.add(self)
        session.commit()

    def delete_from_db(self):
        session = Session()
        session.delete(self)
        session.commit()


Base.metadata.create_all(bind=engine)


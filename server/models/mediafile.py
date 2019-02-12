from sqlalchemy import create_engine, Integer, Column, String, DateTime
from app import Base


class MediaFile(Base):
    """ Media file database entry. Also describes datatable """
    
    __tablename__ = 'Info'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    dt = Column(DateTime)

    def __init__(self, path, dt):
        self.path = path
        self.dt = dt

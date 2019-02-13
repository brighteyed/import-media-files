from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from app import Base


class MediaFile(Base):
    """ Media file. Also describes datatable """
    
    __tablename__ = 'MediaFiles'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    folder = Column(Integer, ForeignKey('MediaDirs.id'))
    timestamp = Column(DateTime)

    def __init__(self, folder, filename, timestamp):
        self.folder = folder
        self.filename = filename
        self.timestamp = timestamp

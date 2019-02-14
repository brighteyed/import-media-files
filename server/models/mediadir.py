from sqlalchemy import Column, Boolean, Integer, String
from app import app_db
from app import Base
from .mediafile import MediaFile


class MediaDir(Base):
    """ Directory with media files. Also describes datatable """
    
    __tablename__ = 'MediaDirs'

    id = Column(Integer, primary_key=True)
    folder_basename = Column(String)
    display_name = Column(String)
    is_album = Column(Boolean)

    media_files = app_db.relationship("MediaFile", order_by=MediaFile.timestamp, lazy='dynamic')

    def __init__(self, folder_basename, display_name, is_album):
        self.folder_basename = folder_basename
        self.display_name = display_name
        self.is_album = is_album

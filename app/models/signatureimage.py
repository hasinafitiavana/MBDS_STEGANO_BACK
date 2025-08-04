from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from app.models import Base

class SignatureImage(Base):
    __tablename__ = "signature_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    signature = Column(String(500), nullable=False)
    datesignature = Column(Date, default=date.today, nullable=False)
    
    # Relation avec User
    user = relationship("User", back_populates="signatures")
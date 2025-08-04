from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, nullable=False, index=True)
    mdp = Column(String(255), nullable=False)

    # Relation avec SignatureImage
    signatures = relationship("SignatureImage", back_populates="user")

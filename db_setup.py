import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class CryptoConfig(Base):
    """Stores the persistent salt for PBKDF2 key derivation."""
    __tablename__ = 'crypto_config'
    
    id = Column(Integer, primary_key=True, default=1)
    master_salt = Column(LargeBinary, nullable=False)
    pbkdf2_iters = Column(Integer, default=480000)

class VaultEntry(Base):
    """Stores the encrypted passwords and ML metadata."""
    __tablename__ = 'vault_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_label = Column(String, nullable=False)
    encrypted_blob = Column(LargeBinary, nullable=False)
    
    strength_score = Column(Integer)
    entropy_bits = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db(db_path="vault.db"):
    """Initializes the SQLite database and returns a session factory."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    session = Session()
    # Ensure a single, secure master salt exists on first run
    config = session.query(CryptoConfig).filter_by(id=1).first()
    if not config:
        new_salt = os.urandom(16)
        new_config = CryptoConfig(master_salt=new_salt)
        session.add(new_config)
        session.commit()
    session.close()
    
    return Session

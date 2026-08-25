import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class CryptoConfig(Base):
    __tablename__ = 'crypto_config'
    id = Column(Integer, primary_key=True, default=1)
    master_salt = Column(LargeBinary, nullable=False)
    pbkdf2_iters = Column(Integer, default=480000)

class VaultEntry(Base):
    __tablename__ = 'vault_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_label = Column(String, nullable=False)
    encrypted_blob = Column(LargeBinary, nullable=False)
    strength_score = Column(Integer)
    entropy_bits = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db(db_name="vault.db"):
    """Initializes the SQLite database in the secure user AppData folder."""
    app_data_dir = os.getenv('APPDATA')
    if not app_data_dir:
        app_data_dir = os.path.expanduser('~')
        
    passcraft_dir = os.path.join(app_data_dir, "PassCraft")
    if not os.path.exists(passcraft_dir):
        os.makedirs(passcraft_dir)
        
    db_path = os.path.join(passcraft_dir, db_name)
    
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    session = Session()
    config = session.query(CryptoConfig).filter_by(id=1).first()
    if not config:
        new_salt = os.urandom(16)
        new_config = CryptoConfig(master_salt=new_salt)
        session.add(new_config)
        session.commit()
    session.close()
    
    return Session

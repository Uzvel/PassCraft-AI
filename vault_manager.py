from db_setup import VaultEntry

def add_vault_entry(session, service_label, encrypted_blob, strength_score, entropy_bits):
    new_entry = VaultEntry(
        service_label=service_label,
        encrypted_blob=encrypted_blob,
        strength_score=strength_score,
        entropy_bits=entropy_bits
    )
    session.add(new_entry)
    session.commit()
    return new_entry.id

def get_all_vault_labels(session):
    entries = session.query(VaultEntry.id, VaultEntry.service_label).all()
    return [{"id": e.id, "label": e.service_label} for e in entries]

def get_encrypted_blob(session, entry_id):
    entry = session.query(VaultEntry).filter_by(id=entry_id).first()
    if entry:
        return entry.encrypted_blob
    return None

def delete_vault_entry(session, entry_id):
    entry = session.query(VaultEntry).filter_by(id=entry_id).first()
    if entry:
        session.delete(entry)
        session.commit()
        return True
    return False

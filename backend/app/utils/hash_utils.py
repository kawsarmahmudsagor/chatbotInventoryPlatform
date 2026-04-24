import hashlib


def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def should_embed(document_path: str, stored_hash: str | None):
    """
    Returns:
        (should_reembed: bool, new_hash: str)
    """
    current_hash = get_file_hash(document_path)

    if not stored_hash:
        return True, current_hash

    return current_hash != stored_hash, current_hash
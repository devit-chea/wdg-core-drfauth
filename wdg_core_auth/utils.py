def parse_verify_key(key: str):
    if not key:
        return None
    return key.replace(r"\n", "\n")
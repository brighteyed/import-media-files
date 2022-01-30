import hashlib


def hash(file) -> str:
    """Returns SHA256 of first 2MB of file contents"""

    BUF_SIZE = 2000000
    with open(file, 'rb') as f:
        data = f.read(BUF_SIZE)
        if data:
            sha256 = hashlib.sha256()
            sha256.update(data)

            return sha256.hexdigest()

    return ""


def equal(fst, snd) -> bool:
    """Returns if files are equal by calculating their hash"""
    return hash(fst) == hash(snd)

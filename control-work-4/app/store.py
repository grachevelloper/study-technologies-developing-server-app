from itertools import count
from threading import Lock


db: dict[int, dict] = {}
_id_seq = count(start=1)
_id_lock = Lock()


def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)


def reset_user_store() -> None:
    global _id_seq
    with _id_lock:
        db.clear()
        _id_seq = count(start=1)

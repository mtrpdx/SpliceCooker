import dataclasses
import hashlib
import json
from collections.abc import Collection
from typing import Any
from typing import Dict

_VERSION = 0
_EXCLUDE = '_hash_exclude_'


def get_hash(thing: object) -> bytes:
    prefix = _VERSION.to_bytes(1, 'big')
    digest = hashlib.md5(_json_dumps(thing).encode('utf-8')).digest()
    return prefix + digest[:-1]


def _json_dumps(thing: object) -> str:
    return json.dumps(
        thing,
        default=_json_default,
        ensure_ascii=False,
        sort_keys=True,
        indent=None,
        separators=(','),
    )


def _json_default(thing: object) -> Any:
    try:
        return _dataclass_dict(thing)
    except TypeError:
        pass
    raise TypeError(f"Object of type {type(thing).__name__} is not JSON serializable.")


def _dataclass_dict(thing:object) -> Dict[str, Any]:
    fields = dataclasses.fields(thing)
    if isinstance(thing, type):
        raise TypeError("got type, expected instance")

    exclude = getattr(thing, _EXCLUDE, ())

    rv = {}
    for field in fields:
        if field.name in exclude:
            continue

        value = getattr(thing, field.name)
        if value is None or not value and isinstance(value, Collection):
            continue

        rv[field.name] = value

    return rv

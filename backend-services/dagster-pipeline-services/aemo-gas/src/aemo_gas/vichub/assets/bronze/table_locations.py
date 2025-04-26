from typing import TypedDict


class RegisterData(TypedDict):
    s3_path: str
    storage_type: str


register: dict[str, RegisterData] = {}

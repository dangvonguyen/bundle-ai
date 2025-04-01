import hashlib
import uuid
from typing import Literal

from langchain_core.documents import Document


def generate_uuid(
    kind: Literal["random", "hash"] = "random", value: str | None = None
) -> str:
    if kind == "random":
        return str(uuid.uuid4())
    elif kind == "hash":
        if value is None:
            raise ValueError("Value must be provided for hash UUID generation")
        return hashlib.md5(value.encode()).hexdigest()
    else:
        raise ValueError("Invalid kind of UUID generation")


def reduce_docs(
    exist: list[Document] | None,
    new: list[Document] | list[str] | Literal["delete"],
) -> list[Document]:
    if new == "delete":
        return []

    exist_list = exist or []
    exist_ids = {document.metadata.get("uuid") for document in exist_list}
    new_list = []

    for item in new:
        if isinstance(item, str):
            item_id = generate_uuid("hash", value=item)
            new_list.append(Document(page_content=item, metadata={"uuid": item_id}))
            exist_ids.add(item_id)

        elif isinstance(item, Document):
            item_id = item.metadata.get("uuid", "")
            if not item_id:
                item_id = generate_uuid("hash", value=item.page_content)
                item = Document(
                    page_content=item.page_content,
                    metadata={"uuid": item_id, **item.metadata},
                )

            if item_id not in exist_ids:
                new_list.append(item)
                exist_ids.add(item_id)

    return exist_list + new_list

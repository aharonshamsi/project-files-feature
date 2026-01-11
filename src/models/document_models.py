from pydantic import BaseModel
from typing import List, Literal, Optional


class Metadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None


class TableData(BaseModel):
    headers: List[str]
    rows: List[List[str]]


class ImageData(BaseModel):
    image_path: str

 
class ContentBlock(BaseModel):
    block_id: int
    type: Literal["heading", "paragraph", "table", "url", "image"] 
    text: str
    table_data: Optional[TableData] = None
    image_data: Optional[ImageData] = None


class DocumentModel(BaseModel):
    metadata: Metadata
    content_blocks: List[ContentBlock]

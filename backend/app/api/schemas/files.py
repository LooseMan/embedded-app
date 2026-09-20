"""Schemas for file-related endpoints."""

from pydantic import BaseModel, ConfigDict


class FileCategoryCreate(BaseModel):
    name: str


class FileCategoryUpdate(BaseModel):
    name: str | None = None


class FileCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class FileCreate(BaseModel):
    category_id: int
    url: str
    size: int


class FileUpdate(BaseModel):
    category_id: int | None = None
    url: str | None = None
    size: int | None = None


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    url: str
    size: int


class FileSetCreate(BaseModel):
    name: str


class FileSetUpdate(BaseModel):
    name: str | None = None


class FileSetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class FileSetRelCreate(BaseModel):
    file_set_id: int
    file_id: int


class FileSetRelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_set_id: int
    file_id: int

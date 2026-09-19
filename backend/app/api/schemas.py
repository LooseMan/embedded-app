"""Pydantic models used at the HTTP boundary."""

from pydantic import BaseModel


class AddRequest(BaseModel):
    a: int
    b: int


class AddResponse(BaseModel):
    result: int

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StripModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class BulkCreateRead(BaseModel):
    created: int

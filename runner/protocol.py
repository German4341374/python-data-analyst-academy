"""Validate all values crossing from the attacker-controlled worker to the API."""

import base64
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator


class Line(BaseModel):
    x: list[str] = Field(max_length=1000)
    y: list[FiniteFloat] = Field(max_length=1000)


class Result(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["dataframe", "array", "scalar", "plot", "none"]
    columns: list[str] | None = Field(default=None, max_length=30)
    data: list | FiniteFloat | None = None
    title: str = Field(default="", max_length=300)
    xlabel: str = Field(default="", max_length=300)
    ylabel: str = Field(default="", max_length=300)
    lines: list[Line] = Field(default_factory=list, max_length=10)
    image: str | None = Field(default=None, max_length=350000)

    @model_validator(mode="after")
    def valid_shape(self) -> "Result":
        if self.type == "dataframe":
            if self.columns is None or not isinstance(self.data, list) or len(self.data) > 1000:
                raise ValueError("Invalid table")
            for row in self.data:
                if not isinstance(row, list) or len(row) != len(self.columns):
                    raise ValueError("Invalid row")
                if any(not isinstance(v, (str, int, float, bool, type(None))) for v in row):
                    raise ValueError("Invalid cell")
        if self.type == "array" and (not isinstance(self.data, list) or len(self.data) > 1000):
            raise ValueError("Invalid array")
        if self.image:
            image_bytes = base64.b64decode(self.image, validate=True)
            if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("Only PNG previews are accepted")
        return self


class WorkerResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)
    result: Result | None = None
    mutated: bool | None = None
    stdout: str = Field(default="", max_length=8192)
    stderr: str = Field(default="", max_length=8192)
    error: str | None = Field(default=None, max_length=100)
    message: str = Field(default="", max_length=1000)

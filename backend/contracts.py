from datetime import date
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

Topic = Literal["documents", "work", "social"]
ResponseMode = Literal["direct", "steps"]
AnswerStatus = Literal["empty", "unsupported", "ambiguous", "matched"]


class SourceReference(BaseModel):
    title: str
    url: HttpUrl
    reviewedAt: str | None

    @field_validator("url")
    @classmethod
    def validate_source_url(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme != "https" or value.username or value.password:
            raise ValueError("Source URLs must use HTTPS without credentials.")
        return value

    @field_validator("reviewedAt")
    @classmethod
    def validate_review_date(cls, value: str | None) -> str | None:
        if value is not None and date.fromisoformat(value).isoformat() != value:
            raise ValueError("Review dates must use YYYY-MM-DD format.")
        return value


class ServiceRecord(BaseModel):
    id: str
    topic: Topic
    title: str
    summary: str
    keywords: list[str]
    agency: str
    channel: Literal["digital", "in-person", "mixed"]
    source: SourceReference
    audience: str
    steps: list[str]
    preparation: list[str]
    limitations: str
    relatedIds: list[str]


class CatalogResponse(BaseModel):
    items: list[ServiceRecord]
    query: str = ""


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(strict=True, max_length=500)
    mode: ResponseMode = "direct"


class AnswerResponse(BaseModel):
    status: AnswerStatus
    message: str
    services: list[ServiceRecord]
    mode: ResponseMode

    @model_validator(mode="after")
    def validate_cardinality(self) -> Self:
        count = len(self.services)
        if self.status == "matched" and count != 1:
            raise ValueError("A matched answer must include exactly one service.")
        if self.status == "ambiguous" and not 2 <= count <= 3:
            raise ValueError("An ambiguous answer must include two or three services.")
        if self.status in {"empty", "unsupported"} and count:
            raise ValueError(
                "An empty or unsupported answer must not include services."
            )
        return self

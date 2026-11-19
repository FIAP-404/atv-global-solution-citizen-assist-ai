from datetime import date
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    AfterValidator,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

Topic = Literal["documents", "work", "social"]
ResponseMode = Literal["direct", "steps"]
AnswerStatus = Literal["empty", "unsupported", "ambiguous", "matched"]


def require_nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError("Response text must not be blank.")
    return value


NonBlankText = Annotated[str, AfterValidator(require_nonblank)]


class SourceReference(BaseModel):
    title: NonBlankText
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
    id: NonBlankText
    topic: Topic
    title: NonBlankText
    summary: NonBlankText
    keywords: list[NonBlankText]
    agency: NonBlankText
    channel: Literal["digital", "in-person", "mixed"]
    source: SourceReference
    audience: NonBlankText
    steps: list[NonBlankText]
    preparation: list[NonBlankText]
    limitations: NonBlankText
    relatedIds: list[NonBlankText]


def require_unique_services(records: list[ServiceRecord]) -> list[ServiceRecord]:
    if len({record.id for record in records}) != len(records):
        raise ValueError("Response service identifiers must be unique.")
    return records


ServiceItems = Annotated[list[ServiceRecord], AfterValidator(require_unique_services)]


class CatalogResponse(BaseModel):
    items: ServiceItems
    query: str = ""


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(strict=True, max_length=500)
    mode: ResponseMode = "direct"


class AnswerResponse(BaseModel):
    status: AnswerStatus
    message: NonBlankText
    services: ServiceItems
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

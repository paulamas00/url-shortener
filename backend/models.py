"""
Database models and API schemas.

- URL is the database table: one row per shortened link.
- URLCreate / URLInfo are the shapes of the JSON the API accepts and returns
  (Pydantic models). Keeping them separate from the table is good practice:
  the client never sets internal fields like the id or the click counter.
"""

from datetime import datetime, timezone

from sqlmodel import SQLModel, Field
from pydantic import BaseModel, HttpUrl


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class URL(SQLModel, table=True):
    """A stored short link: the mapping from short code -> original URL."""

    id: int | None = Field(default=None, primary_key=True)
    short_code: str = Field(index=True, unique=True)
    target_url: str
    clicks: int = Field(default=0)
    created_at: datetime = Field(default_factory=_utcnow)


class URLCreate(BaseModel):
    """What the client sends to create a short link."""

    target_url: HttpUrl  # Pydantic validates this is a real http(s) URL


class URLInfo(BaseModel):
    """What the API returns after creating (or looking up) a short link."""

    short_code: str
    target_url: str
    clicks: int
    created_at: datetime

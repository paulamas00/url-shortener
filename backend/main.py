"""
URL shortener API (FastAPI).

Endpoints:
    POST /api/shorten     -> create a short link, returns its code
    GET  /api/stats/{code}-> look up a link's info + click count
    GET  /{code}          -> redirect to the original URL (and count the click)

Run locally with:
    uvicorn main:app --reload
"""

import secrets
import string

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from database import init_db, get_session
from models import URL, URLCreate, URLInfo

app = FastAPI(title="URL Shortener")

# CORS lets the React frontend (running on a different port during development)
# call this API from the browser without being blocked.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for a real deployment, restrict this to your domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# Characters used to build the random short code (no confusing 0/O, 1/l).
_ALPHABET = string.ascii_letters + string.digits
_CODE_LENGTH = 6


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def _generate_code(session: Session) -> str:
    """Generate a random code that isn't already taken."""
    while True:
        code = "".join(secrets.choice(_ALPHABET) for _ in range(_CODE_LENGTH))
        existing = session.exec(select(URL).where(URL.short_code == code)).first()
        if existing is None:
            return code


@app.post("/api/shorten", response_model=URLInfo)
def shorten(payload: URLCreate, session: Session = Depends(get_session)) -> URL:
    """Create a new short link for the given target URL."""
    code = _generate_code(session)
    url = URL(short_code=code, target_url=str(payload.target_url))
    session.add(url)
    session.commit()
    session.refresh(url)
    return url


@app.get("/api/stats/{code}", response_model=URLInfo)
def stats(code: str, session: Session = Depends(get_session)) -> URL:
    """Return info and click count for a short link."""
    url = session.exec(select(URL).where(URL.short_code == code)).first()
    if url is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return url


@app.get("/{code}")
def redirect(code: str, session: Session = Depends(get_session)) -> RedirectResponse:
    """Redirect a short code to its original URL and count the visit."""
    url = session.exec(select(URL).where(URL.short_code == code)).first()
    if url is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    url.clicks += 1
    session.add(url)
    session.commit()
    return RedirectResponse(url.target_url)

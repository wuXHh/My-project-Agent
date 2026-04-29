from __future__ import annotations

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401


def main() -> None:
    settings.ensure_dirs()
    Base.metadata.create_all(bind=engine)
    print("DB initialized.")


if __name__ == "__main__":
    main()


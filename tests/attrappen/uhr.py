"""Attrappe für die Uhr: liefert eine feste Zeit, die sich von Hand vorstellen lässt."""

from datetime import UTC, datetime, timedelta


class FesteUhr:
    def __init__(self, start: datetime = datetime(2026, 10, 8, 9, 0, tzinfo=UTC)) -> None:
        self.zeit = start

    def __call__(self) -> datetime:
        return self.zeit

    def vorstellen(self, sekunden: float) -> None:
        self.zeit += timedelta(seconds=sekunden)

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Result:
    success: bool
    message: str | None = None


SUCCESS = Result(success=True)


def failure(message: str) -> Result:
    return Result(success=False, message=message)

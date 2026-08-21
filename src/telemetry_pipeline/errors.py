class TelemetryError(Exception):
    """Base exception for expected telemetry pipeline failures."""


class InputValidationError(TelemetryError):
    """Raised when an input file or record violates the telemetry schema."""

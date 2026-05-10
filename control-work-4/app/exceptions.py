from __future__ import annotations

from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "application_error"
    message = "Application error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message


class BusinessRuleViolation(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "business_rule_violation"
    message = "Required business condition was not met"


class ResourceMissing(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "resource_missing"
    message = "Requested resource was not found"

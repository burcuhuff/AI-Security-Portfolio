# secure-enterprise-mcp/server/security/approval.py
"""
Human approval control plane primitives for sensitive MCP actions.

Security properties:
- Approval records are immutable.
- Approval is bound to the exact principal, tool, document, and destination.
- Approval decisions are attributable for audit purposes.
- Approval is not exposed through the agent accessible MCP tool surface.
- Approved actions are single use and protected against concurrent replay.
"""
import server.audit.logger as audit_logger
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import RLock
from typing import Callable
from uuid import uuid4

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    CONSUMED = "CONSUMED"


class ApprovalError(Exception):
    """Raised when an approval request violates approval policy."""


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str

    principal_id: str
    tool_name: str
    document_id: str
    destination: str

    status: ApprovalStatus

    created_at: datetime
    expires_at: datetime

    decided_by: str | None = None
    decided_at: datetime | None = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

def _log_approval_event(
    request: ApprovalRequest,
    *,
    event_type: str,
    outcome: str,
    details: dict | None = None,
    user_id: str | None = None,
    tool_name: str | None = None,
    resource_id: str | None = None,
) -> None:
    event_details = {
        "approval_id": request.approval_id,
        "destination": request.destination,
    }

    if details:
        event_details.update(details)

    audit_logger.log_security_event(
        event_type=event_type,
        outcome=outcome,
        user_id=user_id or request.principal_id,
        tool_name=tool_name or request.tool_name,
        resource_id=resource_id or request.document_id,
        details=event_details,
    )

# the store is in memory (not for prod) 
# TODO: replace in-memory with persistent storage and transactional semantics
class ApprovalStore:

    def __init__(
        self,
        clock: Callable[[], datetime] = _utc_now,
    ):
        self._requests: dict[str, ApprovalRequest] = {}
        self._clock = clock
        self._lock = RLock()

# clock - security controls planned to support expiration in deterministic way
    def create(
        self,
        principal_id: str,
        tool_name: str,
        document_id: str,
        destination: str,
        ttl: timedelta = timedelta(minutes=5),
    ) -> ApprovalRequest:

        if ttl <= timedelta(0):
            raise ApprovalError("Approval TTL must be positive.")

        now = self._clock()

        # "PENDING" - creating the approval shouldn't authorize anything
        request = ApprovalRequest(
            approval_id=f"apr_{uuid4().hex}",
            principal_id=principal_id,
            tool_name=tool_name,
            document_id=document_id,
            destination=destination,
            status=ApprovalStatus.PENDING,
            created_at=now,
            expires_at=now + ttl,
        )

        with self._lock:
            self._requests[request.approval_id] = request

        _log_approval_event(
            request,
            event_type="approval_request",
            outcome="pending",
            details={
                "expires_at": request.expires_at.isoformat(),
            },
        )

        return request

    # retrival helper
    def _get(self, approval_id: str) -> ApprovalRequest:
        try:
            return self._requests[approval_id]
        except KeyError:
            raise ApprovalError(
                f"Unknown approval request: {approval_id}"
            )
    # expiration
    def _expire_if_needed(
        self,
        request: ApprovalRequest,
    ) -> ApprovalRequest:

        if (
            request.status in {
                ApprovalStatus.PENDING,
                ApprovalStatus.APPROVED,
            }
            and self._clock() >= request.expires_at
        ):
            request = replace(
                request,
                status=ApprovalStatus.EXPIRED,
            )

            self._requests[request.approval_id] = request

            _log_approval_event(
                request,
                event_type="approval_expiration",
                outcome="expired",
            )

        return request
    
    # approval
    def approve(
        self,
        approval_id: str,
        decided_by: str,
    ) -> ApprovalRequest:

        with self._lock:
            request = self._expire_if_needed(
                self._get(approval_id)
            )

            if request.status != ApprovalStatus.PENDING:
                raise ApprovalError(
                    f"Cannot approve request in state "
                    f"{request.status.value}."
                )

            request = replace(
                request,
                status=ApprovalStatus.APPROVED,
                decided_by=decided_by,
                decided_at=self._clock(),
            )

            self._requests[approval_id] = request

            _log_approval_event(
                request,
                event_type="approval_decision",
                outcome="approved",
                details={
                    "decided_by": decided_by,
                },
            )  

            return request

    # denial
    def deny(
        self,
        approval_id: str,
        decided_by: str,
    ) -> ApprovalRequest:

        with self._lock:
            request = self._expire_if_needed(
                self._get(approval_id)
            )

            if request.status != ApprovalStatus.PENDING:
                raise ApprovalError(
                    f"Cannot deny request in state "
                    f"{request.status.value}."
                )

            request = replace(
                request,
                status=ApprovalStatus.DENIED,
                decided_by=decided_by,
                decided_at=self._clock(),
            )

            self._requests[approval_id] = request

            _log_approval_event(
                request,
                event_type="approval_decision",
                outcome="denied",
                details={
                    "decided_by": decided_by,
                },
            )

            return request

    # core function
    def consume(
        self,
        approval_id: str,
        principal_id: str,
        tool_name: str,
        document_id: str,
        destination: str,
    ) -> ApprovalRequest:

        with self._lock:
            request = self._expire_if_needed(
                self._get(approval_id)
            )

            if request.status != ApprovalStatus.APPROVED:
                _log_approval_event(
                    request,
                    event_type="approval_consumption",
                    outcome="blocked",
                    user_id=principal_id,
                    tool_name=tool_name,
                    resource_id=document_id,
                    details={
                        "reason": "invalid_status",
                        "status": request.status.value,
                    },
                )

                raise ApprovalError(
                    f"Approval is not usable in state "
                    f"{request.status.value}."
                )

            if request.principal_id != principal_id:
                _log_approval_event(
                    request,
                    event_type="approval_consumption",
                    outcome="blocked",
                    user_id=principal_id,
                    details={
                        "reason": "principal_mismatch",
                        "approved_principal_id": request.principal_id,
                    },
                )

                raise ApprovalError(
                    "Approval principal does not match request."
                )

            if request.tool_name != tool_name:
                _log_approval_event(
                    request,
                    event_type="approval_consumption",
                    outcome="blocked",
                    user_id=principal_id,
                    tool_name=tool_name,
                    details={
                        "reason": "tool_mismatch",
                        "approved_tool_name": request.tool_name,
                    },
                )

                raise ApprovalError(
                    "Approval tool does not match request."
                )

            if request.document_id != document_id:
                _log_approval_event(
                    request,
                    event_type="approval_consumption",
                    outcome="blocked",
                    user_id=principal_id,
                    tool_name=tool_name,
                    resource_id=document_id,
                    details={
                        "reason": "document_mismatch",
                        "approved_document_id": request.document_id,
                    },
                )

                raise ApprovalError(
                    "Approval document does not match request."
                )

            if request.destination != destination:
                _log_approval_event(
                    request,
                    event_type="approval_consumption",
                    outcome="blocked",
                    user_id=principal_id,
                    tool_name=tool_name,
                    resource_id=document_id,
                    details={
                        "reason": "destination_mismatch",
                        "approved_destination": request.destination,
                        "attempted_destination": destination,
                    },
                )

                raise ApprovalError(
                    "Approval destination does not match request."
                )

            request = replace(
                request,
                status=ApprovalStatus.CONSUMED,
            )

            self._requests[approval_id] = request

            _log_approval_event(
                request,
                event_type="approval_consumption",
                outcome="consumed",
            )

            return request
        
    # safe read access
    def get(
        self,
        approval_id: str,
    ) -> ApprovalRequest:

        with self._lock:
            request = self._expire_if_needed(
                self._get(approval_id)
            )

            return request
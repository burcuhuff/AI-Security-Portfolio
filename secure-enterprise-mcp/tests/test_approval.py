#secure-enterprise-mcp/tests/test_approval.py

from datetime import datetime, timedelta, timezone
from threading import Barrier
from concurrent.futures import ThreadPoolExecutor

import pytest

from server.security.approval import (
    ApprovalError,
    ApprovalStatus,
    ApprovalStore,
)


class FakeClock:
    def __init__(self):
        self.now = datetime(
            2026, 10, 6, 12, 0, tzinfo=timezone.utc
        )

    def __call__(self):
        return self.now

    def advance(self, delta: timedelta):
        self.now += delta


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def store(clock):
    return ApprovalStore(clock=clock)


@pytest.fixture
def pending_request(store):
    return store.create(
        principal_id="analyst",
        tool_name="send_enterprise_document",
        document_id="finance_report.txt",
        destination="partner@example.com",
    )

# test creation doesn't authorize anything
def test_create_starts_pending(pending_request):
    assert pending_request.status == ApprovalStatus.PENDING
    assert pending_request.decided_by is None
    assert pending_request.decided_at is None

# test human approval performs the valid transition
def test_pending_request_can_be_approved(
    store,
    pending_request,
):
    approved = store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    assert approved.status == ApprovalStatus.APPROVED
    assert approved.decided_by == "security_operator"
    assert approved.decided_at is not None

# test human denial is terminal
def test_pending_request_can_be_denied(
    store,
    pending_request,
):
    denied = store.deny(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    assert denied.status == ApprovalStatus.DENIED

    with pytest.raises(ApprovalError):
        store.approve(
            pending_request.approval_id,
            decided_by="security_operator",
        )

# test pending requests expire
def test_pending_request_expires(
    store,
    clock,
    pending_request,
):
    clock.advance(timedelta(minutes=6))

    request = store.get(
        pending_request.approval_id
    )

    assert request.status == ApprovalStatus.EXPIRED

# test approved requests expire
def test_approved_request_expires(
    store,
    clock,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    clock.advance(timedelta(minutes=6))

    request = store.get(
        pending_request.approval_id
    )

    assert request.status == ApprovalStatus.EXPIRED


# test approved can be used once
def test_exact_approved_action_can_be_consumed(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    consumed = store.consume(
        approval_id=pending_request.approval_id,
        principal_id="analyst",
        tool_name="send_enterprise_document",
        document_id="finance_report.txt",
        destination="partner@example.com",
    )

    assert consumed.status == ApprovalStatus.CONSUMED


# test wrong principle is blocked
def test_wrong_principal_cannot_consume_approval(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    with pytest.raises(
        ApprovalError,
        match="principal",
    ):
        store.consume(
            approval_id=pending_request.approval_id,
            principal_id="restricted_user",
            tool_name="send_enterprise_document",
            document_id="finance_report.txt",
            destination="partner@example.com",
        )

# test wring tool is blocked
def test_wrong_tool_cannot_consume_approval(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    with pytest.raises(
        ApprovalError,
        match="tool",
    ):
        store.consume(
            approval_id=pending_request.approval_id,
            principal_id="analyst",
            tool_name="delete_enterprise_document",
            document_id="finance_report.txt",
            destination="partner@example.com",
        )

# test wrong document is blocked
def test_wrong_document_cannot_consume_approval(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    with pytest.raises(
        ApprovalError,
        match="document",
    ):
        store.consume(
            approval_id=pending_request.approval_id,
            principal_id="analyst",
            tool_name="send_enterprise_document",
            document_id="customer_secrets.txt",
            destination="partner@example.com",
        )

# test wrong destination is blocked
def test_wrong_destination_cannot_consume_approval(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    with pytest.raises(
        ApprovalError,
        match="destination",
    ):
        store.consume(
            approval_id=pending_request.approval_id,
            principal_id="analyst",
            tool_name="send_enterprise_document",
            document_id="finance_report.txt",
            destination="attacker@example.com",
        )


# test tempered (and failed) doesn't change approved
# TODO: make sure to add this in audit and security event
def test_mismatched_attempt_does_not_consume_valid_approval(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    with pytest.raises(ApprovalError):
        store.consume(
            approval_id=pending_request.approval_id,
            principal_id="analyst",
            tool_name="send_enterprise_document",
            document_id="finance_report.txt",
            destination="attacker@example.com",
        )

    request = store.get(
        pending_request.approval_id
    )

    assert request.status == ApprovalStatus.APPROVED


# test single use (approval ID replay -> BLOCK)
def test_consumed_approval_cannot_be_replayed(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    kwargs = dict(
        approval_id=pending_request.approval_id,
        principal_id="analyst",
        tool_name="send_enterprise_document",
        document_id="finance_report.txt",
        destination="partner@example.com",
    )

    store.consume(**kwargs)

    with pytest.raises(
        ApprovalError,
        match="CONSUMED",
    ):
        store.consume(**kwargs)

# test concurrency
def test_concurrent_consumers_cannot_reuse_same_approval(
    store,
    pending_request,
):
    store.approve(
        pending_request.approval_id,
        decided_by="security_operator",
    )

    barrier = Barrier(2)

    def attempt_consume():
        barrier.wait()

        try:
            store.consume(
                approval_id=pending_request.approval_id,
                principal_id="analyst",
                tool_name="send_enterprise_document",
                document_id="finance_report.txt",
                destination="partner@example.com",
            )
            return "success"

        except ApprovalError:
            return "blocked"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda _: attempt_consume(),
                range(2),
            )
        )

    assert results.count("success") == 1
    assert results.count("blocked") == 1


# test ttl boundary
def test_non_positive_ttl_is_rejected(store):
    with pytest.raises(
        ApprovalError,
        match="TTL",
    ):
        store.create(
            principal_id="analyst",
            tool_name="send_enterprise_document",
            document_id="finance_report.txt",
            destination="partner@example.com",
            ttl=timedelta(0),
        )
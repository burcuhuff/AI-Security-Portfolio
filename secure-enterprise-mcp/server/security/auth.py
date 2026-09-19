# server/security/auth.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    user_id: str
    scopes: frozenset[str]


PRINCIPALS = {
    "analyst": Principal(
        user_id="analyst",
        scopes=frozenset(
            {
                "documents.search",
                "documents.read",
            }
        ),
    ),
    "restricted_user": Principal(
        user_id="restricted_user",
        scopes=frozenset(
            {
                "documents.search",
            }
        ),
    ),
}


def authenticate_user(user_id: str) -> Principal:
    """
    Resolve a demo user identity to its granted scopes.

    In production, this layer would validate an identity token
    and derive scopes from trusted OAuth / Entra claims.
    """

    principal = PRINCIPALS.get(user_id)

    if principal is None:
        raise PermissionError(f"Unknown user: {user_id}")

    return principal
"""Where the engine reads credentials and profile-scoped settings.

The engine never decides where a secret comes from. A host installs a resolver
with :func:`set_secret_resolver`: the Hermes plugin installs
``agent.secret_scope.get_secret`` so every read honours the active Hermes
profile (Hermes plugin catalog rule 11). Without a resolver, :func:`get_secret`
reads the process environment, which is what the MCP server and other
standalone hosts fill from their own configuration.

Every provider key, ``SEARXNG_INSTANCE_URL``, the keyless opt-ins and other
per-profile values are read through :func:`get_secret`. The engine does not
read ``.env`` files itself.
"""
from __future__ import annotations

import os
from typing import Callable, Optional

SecretResolver = Callable[[str, Optional[str]], Optional[str]]

_resolver: Optional[SecretResolver] = None


def set_secret_resolver(resolver: Optional[SecretResolver]) -> None:
    """Install the host's resolver (``None`` returns to the process environment)."""
    global _resolver
    _resolver = resolver


def get_secret_resolver() -> Optional[SecretResolver]:
    return _resolver


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return the value of credential/setting ``name`` for the active scope.

    Errors from the host resolver propagate: a resolver that refuses an unscoped
    read (Hermes multiplexing) must fail the call, not fall back to another
    profile's value in ``os.environ``.
    """
    if _resolver is not None:
        return _resolver(name, default)
    value = os.environ.get(name)
    return value if value is not None else default

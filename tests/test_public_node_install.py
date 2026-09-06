"""Cross-platform invented checks for the platform-specific proof verifier."""

import errno

import pytest

from scripts import verify_public_node_install as verifier


def test_installation_negative_self_checks():
    verifier.self_test()


@pytest.mark.parametrize("error", [errno.ECONNREFUSED, errno.ETIMEDOUT, None])
def test_unreachable_or_available_network_is_not_denial(monkeypatch, error):
    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def settimeout(self, timeout):
            pass

        def connect(self, address):
            if error is not None:
                raise OSError(error, "invented")

    monkeypatch.setattr(verifier.socket, "socket", Connection)
    with pytest.raises(RuntimeError):
        verifier.require_network_denied()


def test_permission_denial_is_accepted(monkeypatch):
    def denied():
        raise OSError(errno.EPERM, "invented permission denial")

    monkeypatch.setattr(verifier.socket, "socket", denied)
    verifier.require_network_denied()

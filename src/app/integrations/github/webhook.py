import hashlib
import hmac


def verify_github_signature(payload: bytes, signature_header: str | None, secret: str) -> bool:
    """Verify X-Hub-Signature-256 using HMAC-SHA256 with constant-time comparison."""
    if not signature_header or not secret:
        return False
    if not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    provided = signature_header[len("sha256=") :]
    return hmac.compare_digest(expected, provided)


__all__ = ["verify_github_signature"]

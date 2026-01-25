"""
URL utilities for normalization and security.
"""

import ipaddress
from urllib.parse import urljoin, urlparse


def normalize_url(url: str, base_url: str) -> str:
    """
    Normalize a URL by resolving relative paths, removing fragments,
    and forcing scheme/domain to lowercase.

    Args:
        url: The URL to normalize (can be relative or absolute)
        base_url: The base URL to resolve relative URLs against

    Returns:
        Normalized absolute URL as a string
    """
    # Resolve relative URLs against base URL
    absolute_url = urljoin(base_url, url)

    # Parse the URL
    parsed = urlparse(absolute_url)

    # Reconstruct URL without fragment
    normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path}"

    # Add query parameters if present
    if parsed.query:
        normalized += f"?{parsed.query}"

    return normalized


def is_safe_url(url: str) -> bool:
    """
    Check if a URL is safe to fetch (SSRF protection).

    Blocks requests to:
    - localhost
    - 127.0.0.0/8 (loopback)
    - 169.254.169.254 (AWS metadata)
    - 10.0.0.0/8 (Class A private)
    - 172.16.0.0/12 (Class B private)
    - 192.168.0.0/16 (Class C private)

    Args:
        url: The URL to check

    Returns:
        True if the URL is safe to fetch, False otherwise
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.netloc.split(":")[0]

        # Block localhost
        if hostname.lower() in ("localhost", "localhost.localdomain"):
            return False

        # Try to parse as IP address
        try:
            ip = ipaddress.ip_address(hostname)

            # Block loopback addresses (127.0.0.0/8)
            if ip.is_loopback:
                return False

            # Block private IP ranges
            if ip.is_private:
                return False

            # Block link-local (169.254.0.0/16)
            if ip.is_link_local:
                return False

            # Block AWS metadata specifically
            if ip == ipaddress.ip_address("169.254.169.254"):
                return False

        except ValueError:
            # Not an IP address, it's a hostname - that's fine
            pass

        return True

    except Exception:
        # If we can't parse the URL, treat it as unsafe
        return False

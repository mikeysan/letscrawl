"""
Tests for URL utilities.
"""

from url_utils import is_safe_url, normalize_url


class TestNormalizeUrl:
    """Test suite for URL normalization."""

    def test_relative_url_resolution(self):
        """Test that relative URLs resolve correctly against base URL."""
        base_url = "https://example.com"
        relative_url = "/about"
        result = normalize_url(relative_url, base_url)
        assert result == "https://example.com/about"

    def test_fragment_removal(self):
        """Test that URL fragments are removed."""
        base_url = "https://example.com"
        url_with_fragment = "https://example.com/page#section"
        result = normalize_url(url_with_fragment, base_url)
        assert result == "https://example.com/page"
        assert "#" not in result

    def test_scheme_and_domain_lowercase(self):
        """Test that scheme and domain are forced to lowercase."""
        base_url = "HTTPS://EXAMPLE.COM"
        result = normalize_url(base_url, base_url)
        assert result == "https://example.com"

    def test_already_absolute_url(self):
        """Test that absolute URLs are preserved."""
        base_url = "https://example.com"
        absolute_url = "https://example.com/page"
        result = normalize_url(absolute_url, base_url)
        assert result == "https://example.com/page"

    def test_relative_path_resolution(self):
        """Test that relative paths resolve correctly."""
        base_url = "https://example.com/dir/"
        relative_path = "subdir/page.html"
        result = normalize_url(relative_path, base_url)
        assert result == "https://example.com/dir/subdir/page.html"

    def test_query_parameter_preservation(self):
        """Test that query parameters are preserved."""
        base_url = "https://example.com"
        url_with_query = "https://example.com/search?q=test"
        result = normalize_url(url_with_query, base_url)
        assert result == "https://example.com/search?q=test"


class TestSSRFProtection:
    """Test suite for SSRF (Server-Side Request Forgery) protection."""

    def test_localhost_blocked(self):
        """Test that localhost URLs are blocked."""
        assert is_safe_url("http://localhost:8000") is False
        assert is_safe_url("https://localhost:443") is False

    def test_127_0_0_1_blocked(self):
        """Test that 127.0.0.1 is blocked."""
        assert is_safe_url("http://127.0.0.1") is False
        assert is_safe_url("http://127.0.0.1:8080") is False

    def test_aws_metadata_blocked(self):
        """Test that AWS metadata endpoint is blocked."""
        assert is_safe_url("http://169.254.169.254") is False
        assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False

    def test_private_ip_ranges_blocked(self):
        """Test that private IP ranges are blocked."""
        # Class A private network
        assert is_safe_url("http://10.0.0.1") is False
        # Class B private network
        assert is_safe_url("http://172.16.0.1") is False
        assert is_safe_url("http://172.31.255.255") is False
        # Class C private network
        assert is_safe_url("http://192.168.1.1") is False

    def test_public_domains_allowed(self):
        """Test that valid public domains are allowed."""
        assert is_safe_url("https://example.com") is True
        assert is_safe_url("https://www.google.com") is True
        assert is_safe_url("http://api.github.com") is True

    def test_public_ips_allowed(self):
        """Test that valid public IPs are allowed."""
        # Google DNS
        assert is_safe_url("http://8.8.8.8") is True
        # Cloudflare DNS
        assert is_safe_url("http://1.1.1.1") is True

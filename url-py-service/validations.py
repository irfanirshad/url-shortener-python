# NEW
from urllib.parse import urlparse
import re
from typing import Optional
import validators
from bleach import clean
import logging


# Check for shell command injection attempts

DANGEROUS_PATTERNS = [
    r'\|\s*sh\b',          # Pipe to shell
    r'\|\s*bash\b',        # Pipe to bash
    r'\b(wget|curl)\b',    # Download commands
    r'\bexec\b',           # exec commands
    r'[;&\n]',             # Command separators
    r'\bcron\b',           # Cron-related
    r'\b(rm|mv|cp)\b',     # File operations
    r'/etc/',              # System directories
    r'\beval\b',           # eval commands
    r'`.*`',               # Backtick execution
    r'\$\(',              # Command substitution
]

def check(url):
    parsed = urlparse(url)
    
    # Block localhost and internal IP addresses
    hostname = url.lower()
    if hostname in ['localhost', '127.0.0.1'] or hostname.startswith('192.168.') or hostname.startswith('10.'):
        
        return False, "Internal/localhost URLs are not allowed"
        
    # Block common shell script extensions
    if any(url.endswith(ext) for ext in ['.sh', '.bash', '.zsh', '.fish']):
        return False, "Shell script URLs are not allowed"
        
    
    
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False, "URL contains potentially dangerous patterns"
            
    return True, None


def is_valid_url_cache(url: str):
    if len(url) > 7:
        return False, "Invalid Cache"
    
    return check(url)

def is_valid_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate URLs against various security criteria.
    Returns (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
        
    # Basic URL cleanup
    url = url.strip()
    url = clean(url)  # Sanitize HTML/scripts
    
    try:
        # Basic URL validation
        if not validators.url(url):
            return False, "Invalid URL format"
            
        return check(url)
        
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

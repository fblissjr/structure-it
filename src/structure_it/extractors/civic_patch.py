"""Patch civic-scraper to be safe."""

import logging
import civic_scraper.platforms.civic_plus.site
from structure_it.utils.safety import DEFAULT_SAFE_SESSION

logger = logging.getLogger(__name__)

def patch_civic_scraper():
    """Monkeypatch civic-scraper to use our SafeSession.
    
    This replaces `requests.get` and `requests.head` in the `site` module
    with our rate-limited, backoff-enabled versions.
    """
    logger.info("Applying safety patch to civic-scraper...")
    
    # The site.py module imports requests as 'requests'
    # We replace the 'get' and 'head' functions on that imported module object
    # Note: We must patch where it is USED, not where it is defined.
    
    # Patch civic_plus.site
    civic_scraper.platforms.civic_plus.site.requests.get = DEFAULT_SAFE_SESSION.get
    civic_scraper.platforms.civic_plus.site.requests.head = DEFAULT_SAFE_SESSION.head
    
    logger.info("Safety patch applied. All civic-scraper requests are now rate-limited.")

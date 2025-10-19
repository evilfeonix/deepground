
# deepground/core.py                  # deepground/core.py                      # deepground/core.py                  # deepground/core.py
# tool        ->      Deepground
# version        ->      v[0.8.2]
# author        ->      Evilfeonix
# date        ->      Sep 16, 2025
# email        ->      evilfeonix@proton.me
# github        ->      https://github.com/evilfeonix
# dics        ->      https://github.com/evilfeonix/deepground
# website        ->      https://evilfeonix.eu.org
# blog        ->      https://evilfeonix.github.io/blog
# youtube        ->      https://youtube.com/@evilfeonix
# latest_update        ->      Sep 17, 2025
# latest_update        ->      Sep 22, 2025
# latest_update        ->      Oct 19, 2025
# comment        ->      3 years of exprience python, yet... this's my first python library, hope you guys will enjoy it.
# status        ->      Deepground is still under maintainers, but can be userd properly.
# feedback        ->      Please! report any bugs found in this script. 
# support        ->      Support us by starring + forking this repos..! follow us on github, sponsor us (if possible).
# contributors        ->      Contributors are welcome to this journey, feel free to comtribute.
# deepground/core.py                  # deepground/core.py                      # deepground/core.py                  # deepground/core.py


"""
Deepground Core
-------------
- synchronous + async fetchers
- Clearnet + darknet search engine 
- optional Tor darknet lookups (via socks5 proxy)
- fetch_context(url) -> readable text (paragraphs + truncated)
- fetch_source(url) -> raw html (truncated)
- async multi_fetch + cache + logging
- robust error handling
"""

from __future__ import annotations
import asyncio
import aiohttp
import hashlib
import json
import os
import time
import httpx
import socket
from httpx_socks import AsyncProxyTransport
from typing import List, Dict, Optional, Any, Tuple, Type
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from ddgs import DDGS

"""Deepground | LLM grounding library.

A metasearch and context-fetching library for both clearnet and darknet sources.  
The Grounder library empowers LLM agents with real-time data access from the net. 
Designed for developers, researchers, hackers, and anyone shaping the future of GenAI.  
Feed Deepground results directly into your LLM agent for grounded, real-world context.
Extract and format Deepground results for better human readability.

Args:
    api (str | None): Not in use yet (reserved for future APIs). Defaults to None.
    proxies (str | None): Proxy for requests. Defaults to None.
    user_agent (str): Custom User Agent for HTTP requests. Defaults to USER_AGENT.
    timeout (int | None): Request timeout in seconds. Defaults to 20.
    cache (bool): Whether to enable result caching. Defaults to True.
    use_tor (bool): Route traffic through Tor for darknet search. Defaults to False.

Examples:
    Synchronous (clearnet):
        >>> from deepground.core import Grounder
        >>> g = Grounder()
        >>> r = g.search("naija latest tech news")
        >>> ctx = g.fetch_context("https://example.com/article")
        >>> src = g.fetch_source("https://example.com/file.txt")

    Synchronous (darknet):
        >>> from deepground.core import Grounder
        >>> g_tor = Grounder(use_tor=True)
        >>> d_r = g_tor.dark_search("proxies combo list")
        >>> d_ctx = g_tor.fetch_context("http://somesite.onion")
        >>> d_src = g_tor.fetch_source("http://somesite.onion/file.txt")

    Asynchronous (clearnet):
        >>> import asyncio
        >>> from deepground.core import GrounderAsync
        >>> async def run():
        ...     ga = GrounderAsync()
        ...     r = await ga.search("naija latest tech news")
        ...     ctx = await ga.fetch_context("https://example.com/article")
        ...     src = await ga.fetch_source("https://example.com/file.txt")
        ...     multi_src = await ga.multi_fetch(["https://a.com", "https://b.org"], context=False)
        >>> asyncio.run(run())

    Asynchronous (darknet):
        >>> import asyncio
        >>> from deepground.core import GrounderAsync
        >>> async def run():
        ...     ga_tor = GrounderAsync(use_tor=True)
        ...     d_r = await ga_tor.dark_search("proxies combo list")
        ...     d_ctx = await ga_tor.fetch_context("http://somesite.onion")
        ...     d_src = await ga_tor.fetch_source("http://somesite.onion/file.txt")
        ...     d_multi_src = await ga_tor.multi_fetch(["http://ss1.onion","http://ss2.onion"], context=True)
        >>> asyncio.run(run())

    LangChain integration:
        >>> from deepground.core import GrounderTool
        >>> gt = GrounderTool()
        >>> r = gt._run("search:naija latest tech news")
        >>> ctx = gt._run("fetch_context:https://example.com/article")
        >>> src = gt._run("fetch_source:https://example.net/file.txt")
        >>> multi_src = gt._run("multi_fetch:https://a.com,https://b.org")

        >>> gt_tor = GrounderTool(use_tor=True)
        >>> d_r = gt_tor._run("dark_search:naija latest tech news")
        >>> d_ctx = gt_tor._run("fetch_context:http://somesite.onion/article")
        >>> d_src = gt_tor._run("fetch_source:http://somesite.onion/file.txt")
        >>> d_multi_src = gt_tor._run("multi_fetch:http://ss1.onion,http://ss2.onion", context=False)
"""

# ------------ Config ------------
TOOL = "Deepground"
VERSION = "0.8.2"
AUTHOR = "evilfeonix"
USER_AGENT = f"{TOOL}/{VERSION} ({AUTHOR}; python3 compatible)"
CACHE_DIR = os.path.expanduser("~/.deepground/cache")
LOG_FILE = os.path.expanduser("~/.deepground/deepground.log")
TOR_SOCKS = "socks5h://127.0.0.1:9050"

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ------------ Core Functions ------------
def _log(msg: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:pass

def _cache_path(key: str) -> str:
    keyh = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{keyh}.json")

def _read_cache(key: str) -> Optional[Dict[str, Any]]:
    path = _cache_path(key)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            _log(f"cache read error for {key}: {e}")
    return None

def _write_cache(key: str, value: Dict[str, Any]):
    path = _cache_path(key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(value, f)
    except Exception as e:
        _log(f"cache write error for {key}: {e}")


# ------------ Sync Wrappers ------------
import requests
from requests.exceptions import RequestException, Timeout, ProxyError, SSLError, ConnectionError

class Grounder:
    """Wrapper for the synchronous version of deepground"""
    def __init__(
        self, 
        api: str | None = None, 
        proxies: str | None = None, 
        user_agent: str = USER_AGENT, 
        use_tor: bool | str = False, 
        timeout: int | None = 20, 
        cache: bool = True
    ):
        self.session = requests.Session()
        self.timeout = timeout
        self.proxies = proxies
        self.api = api
        self.cache = cache
        self.use_tor = use_tor

        TOR_SOCKS = "socks5h://127.0.0.1:9050"
        if self.use_tor:
            TOR_SOCKS = self.use_tor if self.use_tor is not True else TOR_SOCKS
            self.set_proxies = {"http":TOR_SOCKS,"https": TOR_SOCKS}
            self.session.proxies.update(self.set_proxies)
            self.timeout *= 5 
        elif self.proxies:
            self.set_proxies = {"http":self.proxies,"https": self.proxies}
            self.session.proxies.update(self.set_proxies)
            self.timeout *= 2 
        else:
            self.set_proxies = None
            self.session.proxies = None

        user_agent = user_agent if user_agent else USER_AGENT
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1"
        }
        
    def _wrap_requests(self, method: str, url: str, **kwargs) -> Tuple[Optional[requests.Response], Optional[str]]:
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("headers", self.headers)
        
        try:
            if self.use_tor and url=="https://ahmia.fi/search/":
                resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            else:
                resp = self.session.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp, None
        except ProxyError:
            return None, "Proxy/Tor connection error."
        except Timeout:
            return None, f"Timeout when connecting to {url}"
        except SSLError:
            return None, f"SSL error for {url}"
        except ConnectionError:
            try:
                resp = requests.get(
                    url,
                    proxies=self.set_proxies,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=False
                )
                resp.raise_for_status()
                return resp, None
            except Exception as e:
                return None, f"Network error for {url}: {e}"
        except RequestException as e:
            return None, f"HTTP error: {e}"
        except Exception as e:
            return None, f"Unexpected error: {e}"


    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        DDGS | Dux Distributed Global Search: 

        Args:
            query (str): Search query
            limit (int): Max number of results

        Returns:
            dicts: {[{link, title, snippet},...]}
        """

        key = f"search:{query}:{limit}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"results": cached["results"], "cached": True}

        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=limit):
                    results.append({"title": r.get("title"), "link": r.get("href"), "snippet": r.get("body")})
             
        except Exception as e:
            _log(f"search error: {e}")
            return {"error": e}

        if self.cache:
            _write_cache(key, {"results": results, "ts": time.time()})
        return {"results": results}

    def dark_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search Ahmia (onion) index. Requires TOR running and use_tor=True to work reliably.
        Returns {'results': [...]} or {'error': msg}

        Search Ahmia (Tor search engine). 

        Args:
            query (str): Search query
            limit (int): Max number of results
            
        Returns:
            dict: {[{link, title, snippet, ...},...]}

        Important Note: This function pretend to use tor SOCKS
        """

        url = "https://ahmia.fi/search/"
        params = {"q": query} 

        if not self.use_tor:
            _log(f"dark_search err: Dark search requires tor network eg.(use_tor=True)")
            return {"error": "Dark search requires tor network eg.(use_tor=True)"}

        key = f"dark:{query}:{limit}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"results": cached["results"], "cached": True}

        try:
            _res, _err = self._wrap_requests("GET", url, params=params)
            if not _res:
                if "Proxy/Tor" in _err and self.proxies:
                    _log(f"dark_search error: The given proxies ({self.proxies}) is dead")
                    return {"error": f"The given proxies ({self.proxies}) is dead"}

                _log(f"dark_search error: {_err}")
                return {"error": _err}

            results = []
            try:
                soup = BeautifulSoup(_res.text, "html.parser")
                for li in soup.select("li.result")[:limit]:
                    title_tag = li.select_one("h4 a")
                    title = title_tag.get_text(strip=True) if title_tag else None

                    url = None
                    if title_tag and "href" in title_tag.attrs:
                        href = title_tag["href"]
                        parsed = parse_qs(urlparse(href).query)
                        url = parsed.get("redirect_url", [href])[0]

                    snippet_tag = li.select_one("p")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else None

                    cite_tag = li.select_one("cite")
                    cite = cite_tag.get_text(strip=True) if cite_tag else None

                    span = li.select_one("span.lastSeen")
                    last_seen = span.get_text(strip=True).replace('\xa0',' ') if span else None
                    timestamp = span["data-timestamp"] if span and span.has_attr("data-timestamp") else None

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "cite": cite,
                        "ts": f"{last_seen}, {timestamp}"
                    })

                    results = results or {"error": f"No darkweb results found: {query}."}
            except Exception as err:
                return {"error": f"dark_search parsing error: {err}"} # report
        except Exception as e:
            _log(f"dark_search error: {e}")
            return {"error": f"dark_search error: {e}"}

        if self.cache:
            _write_cache(key, {"results": results, "ts": time.time()})
        return {"results": results} 

    def fetch_context(self, url: str, max_chars: int = 3000) -> Dict[str, Any]:
        """Fetch and extract readable paragraphs from URL"""

        if not url.startswith(("http://", "https://")):
            _log(f"fetch_context err: {url} not a valid URL")
            return {"error": f"{url} not a valid URL"}

        if not self.use_tor and (".onion/" in url or url.endswith(".onion")):
            _log(f"fetch_context err: onion sites requires tor network eg.(use_tor=True)")
            return {"error": "onion sites requires tor network eg.(use_tor=True)"}

        # trimmed text: True
        key = f"context:{url}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"url": url, "content": cached["content"], "cached": True}

        _res, _err = self._wrap_requests("GET", url)
        if not _res:
            if "Proxy/Tor" in _err and self.proxies:
                _log(f"content error: The given proxies ({self.proxies}) is dead")
                return {"error": f"The given proxies ({self.proxies}) is dead"}

            _log(f"content error: {_err}")
            return {"error": _err}

        try:
            soup = BeautifulSoup(_res.text, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
            joined = " ".join(paragraphs)
            if not joined:
                # fallback: use body text
                body = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
                joined = body or ""
            if len(joined) > max_chars:
                joined = joined[:max_chars] + "..."

            if self.cache:
                _write_cache(key, {"content": joined, "ts": time.time()})
            return {"url": url, "content": joined}
        except Exception as e:
            _log(f"context_parse error: {e}")
            return {"error": f"parse error: {e}"}

    def fetch_source(self, url: str, max_chars: int = 5000) -> Dict[str, Any]:
        """Fetch raw web(HTML) / file(.css/.js/.txt/e.t.c)"""
        
        if not url.startswith(("http://", "https://")):
            _log(f"fetch_source err: {url} not a valid URL")
            return {"error": f"{url} not a valid URL"}

        if not self.use_tor and (".onion/" in url or url.endswith(".onion")):
            _log(f"fetch_source err: onion sites requires tor network eg.(use_tor=True)")
            return {"error": "onion sites requires tor network eg.(use_tor=True)"}

        key = f"source:{url}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"url": url, "source": cached["source"], "cached": True}

        _res, _err = self._wrap_requests("GET", url)
        if not _res:
            if "Proxy/Tor" in _err and self.proxies:
                _log(f"source error: The given proxies ({self.proxies}) is dead")
                return {"error": f"The given proxies ({self.proxies}) is dead"}

            _log(f"source error: {_err}")
            return {"error": _err}

        try:
            text = _res.text or "EMPTY"
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            if self.cache:
                _write_cache(key, {"source": text, "ts": time.time()})
            return {"url": url, "source": text}
        except Exception as e:
            _log(f"context_source error: {e}")
            return {'error': str(e)}

    # ---- simple utility: is_valid_url ----
    @staticmethod
    def is_valid_url(u: str) -> bool:
        return u.startswith("http://") or u.startswith("https://") or u.endswith(".onion")

# ------------ Async Wrappers ------------
from aiohttp import ClientError, ClientTimeout, ClientConnectorError
from ssl import SSLError

class GrounderAsync:
    """Wrapper for the asynchronous version of deepground
    
    This wrapper using aiohttp for faster parallel fetches.
    And only use it in async contexts:

        async with GrounderAsync(use_tor=True) as g:
          results = await g.fetch_context(url)
    """
    def __init__(
        self, 
        api: str | None = None, 
        proxies: str | None = None, 
        user_agent: str = USER_AGENT, 
        use_tor: bool | str = False, 
        timeout: int | None = 20, 
        cache: bool = True
    ):

        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = timeout
        self.proxies = proxies
        self.api = api
        self.cache = cache
        self.use_tor = use_tor
        TOR_SOCKS = "socks5h://127.0.0.1:9050"

        if self.use_tor:
            # Use socks proxy - requires requests[socks]
            TOR_SOCKS = self.use_tor if self.use_tor != True else TOR_SOCKS
            # self.proxies = TOR_SOCKS
            self.timeout *= 5
        elif self.proxies:
            self.proxies = self.proxies
            self.timeout *= 3
        else:self.proxies = None

        user_agent = user_agent if user_agent else USER_AGENT
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1"
        }    

    async def _wrap_requests(self, method: str, url: str, **kwargs) -> Tuple[Optional[aiohttp.ClientResponse], Optional[str]]:
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("headers", self.headers)
        
        try:
            async with self.session.request(method, url, **kwargs) as resp:
                resp_text = await resp.text()
                if resp.status >= 400:
                    return None, f"HTTP error {resp.status} for {url}"
                resp._text = resp_text 
                return resp, None
        except aiohttp.ClientConnectorError:
            return None, "Connection error"

        except Exception as e:
            return None, f"Unexpected error: {e}"

        except ProxyError:
            return None, "Proxy/Tor connection error."

        except (Timeout, asyncio.TimeoutError):
            return None, f"Timeout when connecting to {url}"

        except SSLError:
            return None, f"SSL error for {url}"

        except (ConnectionError, ConnectionResetError, socket.error) as e:
            return None, f"Tor proxy connection failed. Make sure Tor is running on {TOR_SOCKS} ({e})"

        except RequestException as e:
            return None, f"HTTP error: {e}"

        except Exception as e:
            return None, f"Unexpected error: {type(e).__name__}: {e}"

    async def __aenter__(self): 
        conn = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=conn)
        return self

    async def __aexit__(self, exc_type, exc, tb): 
        if self.session:
            await self.session.close()

    async def _afetch(self, url: str) -> Dict[str, Any]:

        if not self.use_tor: 
            proxies = {"http": self.proxies,"https": self.proxies,}
        else:proxies = {"http": self.use_tor,"https": self.use_tor,}

        try:
            r = requests.get(url, proxies=proxies, headers=self.headers, timeout=self.timeout, allow_redirects=False)
            return {"url": url, "content": r.text}
        except ProxyError as e:
            failureMSG = f"Proxy/Tor connection: {e}"
        except Timeout as e:
            failureMSG = f"Timeout: {e}"
        except SSLError as e:
            failureMSG = f"SSL: {e}"
        except ConnectionError as e: 
            failureMSG = f"Network: {e}"
        except RequestException as e:
            failureMSG = f"HTTP: {e}"
        except Exception as e:
            failureMSG = f"Unexpected: {e}"

        return {"url": url, "error": failureMSG}

    async def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        DDGS | Dux Distributed Global Search: 

        Args:
            query (str): Search query
            limit (int): Max number of results

        Returns:
            dicts: {[{link, title, snippet},...]}
        """

        key = f"search:{query}:{limit}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"results": cached["results"], "cached": True}

        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=limit):
                    results.append({"title": r.get("title"), "link": r.get("href"), "snippet": r.get("body")})
             
        except Exception as e:
            _log(f"async search error: {e}")
            return {"error": e}

        if self.cache:
            _write_cache(key, {"results": results, "ts": time.time()})
        return {"results": results}
        

    async def dark_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search Ahmia (onion) index. Requires use_tor=True to work reliably.
        Returns {'results': [...]} or {'error': msg}

        Search Ahmia (Tor search engine). 

        Args:
            query (str): Search query
            limit (int): Max number of results
            
        Returns:
            dict: {[{link, title, snippet, ...},...]}

        Important Note: This function pretend to use tor SOCKS
        """

        url = "https://ahmia.fi/search/"
        params = {"q": query} 

        if not self.use_tor:
            _log(f"async dark_search error: Dark search requires tor network eg.(use_tor=True)")
            return {"error": "Dark search requires tor network eg.(use_tor=True)"}

        key = f"dark:{query}:{limit}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"results": cached["results"], "cached": True}

        try:
            _res, _err = await self._wrap_requests("GET", url, params=params)
            if not _res:
                if "Proxy/Tor" in _err and self.proxies:
                    _log(f"async dark_search error: The given proxies ({self.proxies}) is dead")
                    return {"error": f"The given proxies ({self.proxies}) is dead"}

                _log(f"async dark_search error: {_err}")
                return {"error": _err}

            results = []
            try:
                soup = BeautifulSoup(await _res.text(), "html.parser")
                for li in soup.select("li.result")[:limit]:
                    title_tag = li.select_one("h4 a")
                    title = title_tag.get_text(strip=True) if title_tag else None

                    url = None
                    if title_tag and "href" in title_tag.attrs:
                        href = title_tag["href"]
                        parsed = parse_qs(urlparse(href).query)
                        url = parsed.get("redirect_url", [href])[0]

                    snippet_tag = li.select_one("p")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else None

                    cite_tag = li.select_one("cite")
                    cite = cite_tag.get_text(strip=True) if cite_tag else None

                    span = li.select_one("span.lastSeen")
                    last_seen = span.get_text(strip=True).replace('\xa0',' ') if span else None
                    timestamp = span["data-timestamp"] if span and span.has_attr("data-timestamp") else None

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "cite": cite,
                        "ts": f"{last_seen}, {timestamp}",
                    })

                    results = results or {"error": f"No darkweb results found: {query}."}
            except Exception as err:
                return {"error": f"async dark_search parsing error: {err}"} # report
        except Exception as e:
            _log(f"async dark_search error: {e}")
            return {"error": f"dark_search error: {e}"}

        if self.cache:
            _write_cache(key, {"results": results, "ts": time.time()})
        return {"results": results}     

    async def fetch_context(self, url: str, max_chars: int = 3000) -> Dict[str, Any]:
        """Fetch and extract readable paragraphs from URL"""
        
        if not url.startswith(("http://", "https://")):
            _log(f"fetch_context err: {url} not a valid URL")
            return {"error": f"{url} not a valid URL"}

        if not self.use_tor and (".onion/" in url or url.endswith(".onion")):
            _log(f"fetch_context err: onion sites requires tor network eg.(use_tor=True)")
            return {"error": "onion sites requires tor network eg.(use_tor=True)"}

        key = f"asynccontext:{url}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"url": url, "content": cached["content"], "cached": True}

        _res = await self._afetch(url)
        if _res.get("error"):
            return _res
        try:
            soup = BeautifulSoup(_res["content"], "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
            joined = " ".join(paragraphs)
            if not joined:
                joined = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
            if len(joined) > max_chars:
                joined = joined[:max_chars] + "..."
            if self.cache:
                _write_cache(key, {"content": joined, "ts": time.time()})
            return {"url": url, "content": joined}
        except Exception as e:
            _log(f"async content_parse error: {e}")
            return {"error": str(e)}

    async def fetch_source(self, url: str, max_chars: int = 5000) -> Dict[str, Any]:
        """Fetch raw web(HTML) / file(.css/.js/.txt/e.t.c)"""
        
        if not url.startswith(("http://", "https://")):
            _log(f"fetch_source err: {url} not a valid URL")
            return {"error": f"{url} not a valid URL"}

        if not self.use_tor and (".onion/" in url or url.endswith(".onion")):
            _log(f"fetch_source err: onion sites requires tor network eg.(use_tor=True)")
            return {"error": "onion sites requires tor network eg.(use_tor=True)"}

        key = f"asyncsource:{url}"
        if self.cache:
            cached = _read_cache(key)
            if cached:
                return {"url": url, "source": cached["source"], "cached": True}

        _res = await self._afetch(url)
        if _res.get("error"):
            return _res

        try:
            text = _res.get("content", "EMPTY")
            if len(text) > max_chars:
                text = text[:max_chars] + "..."

            if self.cache:
                _write_cache(key, {"source": text, "ts": time.time()})
            return {"url": url, "source": text}
        except Exception as e:
            _log(f"async source_parse error: {e}")
            return {"error": str(e)}

    async def multi_fetch(self, urls: List[str], context: bool = True) -> List[Dict[str, Any]]:
        """Fetch multiple url concurrently: This returnd list of all urls fetch results"""
        tasks = []
        for u in urls:
            tasks.append(self.fetch_context(u) if context else self.fetch_source(u))
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return results
    
    
# ------------ Langchain Wrappers ------------
from langchain.tools import BaseTool

class GrounderTool(BaseTool):
    """LangChain tool integration for Deepground (clearnet + darknet search & fetch)."""

    name: str = "grounder_tool"
    description: str = """
    Deepground (GrounderTool) - LLM internet fetcher (supports clearnet & darknet).
    Available commands:
      - search:<query>        → Clearnet search
      - dark_search:<query>   → Darknet search (requires Tor)
      - fetch_context:<url>   → Extract readable paragraphs from URL
      - fetch_source:<url>    → Fetch raw HTML/text from URL
      - multi_fetch:<url1,url2,...> → Fetch multiple URLs concurrently
    """

    api: Optional[str] = None
    proxies: Optional[str] = None
    user_agent: str = USER_AGENT
    use_tor: bool | str = False, 
    timeout: int = 20
    cache: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _dispatch(self, g: GrounderAsync, query: str):
        """
        Run GrounderAsync methods in LangChain pipelines.
        Args:
            query: string in format "action:payload"
                   e.g. "search:latest AI news"
        """
        try:
            if ":" not in query:
                _log(f"dispatch (langchain): Invalid input format. Use 'action:payload'.")
                return {"error": "Invalid input format. Use 'action:payload'."}

            if query.startswith("search:"):
                return await g.search(query.split(":", 1)[1].strip())
            elif query.startswith("dark_search:"):
                return await g.dark_search(query.split(":", 1)[1].strip())
            elif query.startswith("fetch_context:"):
                return await g.fetch_context(query.split(":", 1)[1].strip())
            elif query.startswith("fetch_source:"):
                return await g.fetch_source(query.split(":", 1)[1].strip())
            elif query.startswith("multi_fetch:"):
                urls = [u.strip() for u in query.split(":", 1)[1].split(",")]
                return await g.multi_fetch(urls, context=True)
            else:
                _log(f"dispatch (langchain): Unknown action '{query}'")
                return {"error": f"Unknown action '{query}'"}
        except Exception as e:
            _log(f"dispatch (langchain): {e}")
            return {"error": str(e)}

    async def _arun(self, query: str):
        async with GrounderAsync(
            api=self.api,
            proxies=self.proxies,
            user_agent=self.user_agent,
            use_tor=self.use_tor,
            timeout=self.timeout,
            cache=self.cache,
        ) as g:
            try:
                return await self._dispatch(g, query)
            except Exception as e:
                _log(f"_arun (langchain): {e}")
                return {"error": str(e)}

    def _run(self, query: str):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:loop = None

        if loop and loop.is_running():return loop.create_task(self._arun(query))  # If already inside an event loop (e.g., Jupyter, LangChain agent)
        else:return asyncio.run(self._arun(query))  # Safe for normal scripts

#     async def _arun(self, query: str, **kwargs: Any) -> str:
#         """Async is not implemented yet for LangChain integration."""
#         raise NotImplementedError("Use GrounderAsync directly for async calls.")
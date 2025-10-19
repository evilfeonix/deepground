# Deepground
<div align=center>

[![Deepground](https://github.com/evilfeonix/deepground/banner.png)](https://www.python.org/)

Deepground – Clearnet + Darknet Search & Fetcher

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Version](https://img.shields.io/badge/VERSION-0.8.1.svg)](https://github.com/evilfeonix/deepground) 
[![Repo Size](https://img.shields.io/github/repo-size/evilfeonix/deepground)](https://github.com/evilfeonix/deepground)  
[![Stars](https://img.shields.io/github/stars/evilfeonix/deepground?style=social)](https://github.com/evilfeonix/deepground/stargazers)  
[![Forks](https://img.shields.io/github/forks/evilfeonix/deepground?style=social)](https://github.com/evilfeonix/deepground/network/members)  
</div>

Deepground - this is a Python library that empowers LLM agents with real-time data access from buth the clearnet and darknet.\
This library is design for developers, hackers, pentesters, researchers,  and AI agents who need real-time datas from both the clearnet and darknet to their CLI.


## Overview
The deepground project was developed by evilfeonix and designed to evaluate the performance of llm and their applications. It gives your LLM the power to access and monitor real-time data from the net for free without limitation or restriction.
<!-- gpt: add more overview of the grounder project here -->


## Features
- Support sync / async(parallel fetching) mode, depending on your workflow.
- Fetch context and extract sources (raw HTML/code/text) from URLs.
- Integrate seamlessly with LangChain and other LLM frameworks.
- Searches across clearnet/darknet sources with ease.
- Built-in caching + logging
- Error handling

 
## Installation
```bash
pip install deepground
```

For dev:
```bash
git clone https://github.com/evilfeonix/deepground.git
cd deepground
pip install -e .
python3 run.py
```

## Usage
### Simple Usage:
```py
from deepground.core import Grounder

g = Grounder()
print(g.search("latest AI news"))

g_tor = Grounder(use_tor=True)
print(g_tor.dark_search("leaked databases"))
```

### Synchronous:
```py
from deepground.core import Grounder


# Clearnet search
g = Grounder(use_tor=False)
r = g.search("Python hacking", limit=3)
print(r)

# Darknet search
g_tor = Grounder(use_tor=True)
d_r = g_tor.dark_search("market", limit=3)
print(d_r)

# Fetch readable content (page)
p = g.fetch_context("https://example.com")
print(p["content"])

# Fetch row source (code/text)
s = g_tor.fetch_source("https://somesite.onion/ABCDEF.txt")
print(s["source"])
```

### Asynchronous:
```py
import asyncio
from deepground.core import GrounderAsync

async def main():
    async with GrounderAsync(use_tor=False) as g:
        results = await g.search("cybersecurity news", limit=3)
        print(results)

        source = await g.multi-fetch("https://example.com,https://example.net", context=False)
        print(source["source"][:300])

asyncio.run(main())
```

### LangChain Integration:
```py
from deepground.core import GrounderTool

tool = GrounderTool(use_tor=True)

print(tool._run("search:latest AI news"))
print(tool._run("dark_search:proxies combo list"))
print(tool._run("fetch_context:https://github.com"))
print(tool._run("fetch_source:https://somesite.onion"))
print(tool._run("multi-fetch:https://ss1.onion,https://ss2.onion"))
```

## Langchain Agent
Feed results directly into your LLM agents for grounded, real-world context:
```py
from deepground.core import Grounder

# Clearnet search
g = Grounder()
res = g.search("naija latest tech news")
ctx = g.fetch_context("https://example.com/article")

# Darknet search with Tor
g_tor = Grounder(use_tor=True)
d_res = g_tor.dark_search("fresh proxies list")
d_ctx = g_tor.fetch_context("http://somesite.onion/article")

# Feed into LLM

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

answer = llm.invoke(f"Summarize:\n\n{ctx}")
print(answer)

```

## For darknet features:

TOR running locally (socks5://127.0.0.1:9050)
```bash
pip install requests[socks]
```

## Logging & Caching
```bash
Cache stored at: ~/.deepground/cache
Log file: ~/.deepground/deepground.log
```

## Documentation
Detailed documentation includeing full guides, and examples can be found at our official website https://evilfeonix.eu.org 

## Contrubuting
Contributors are welcome to this journey, feel free to :
- Report bugs via github issues.
- Suggest feature with use cases.
- Submit PRs with clear description.

## Disclaimer

> _This library is for educational and research purposes only. Authors will never ever be responsible for any misuse or damage cause by this project._



## LICENSE
Use MIT license:
```text
MIT License
Copyright (c) 2025 Evilfeonix
Permission is hereby granted, free of charge...
```

## Powered by
This project is made posibly thanks to those infrastructure with their generous supports.

[![OpenAI](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Ahmia](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DDGS](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)  
[![PyPI](https://img.shields.io/pypi/v/deepground-evilfeonix.svg)](https://pypi.org/project/deepground-evilfeonix/)  
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)  



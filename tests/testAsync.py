# tests/testAsync.py
import asyncio
from deepground.core import GrounderAsync

async def run():
    ga = GrounderAsync()
    r = await ga.search("naija latest tech news")
    ctx = await ga.fetch_context("https://example.com/article")
    src = await ga.fetch_source("https://example.com/file.txt")
    multi_src = await ga.multi_fetch(["https://a.com", "https://b.org"])

    # Feed the results straightly to your llm agent
    # But for human readability! dev will need to extract and format the original results
    
    for idx in r["results"]:
        for k,v in idx.items():
            print(f"{k}: {v}\n")

                # OR

    for idx in r["results"]:
        print(f"Link: {idx['url']}")
        print(f"Topic: {idx['title']}")
        print(f"Snippet: {idx['snippet']}")
    asyncio.run(run())

async def run():
    ga_tor = GrounderAsync(use_tor=True)
    d_r = await ga_tor.dark_search("proxies combo list")
    d_ctx = await ga_tor.fetch_context("http://somesite.onion")
    d_src = await ga_tor.fetch_source("http://somesite.onion/file.txt")
    d_multi_src = await ga_tor.multi_fetch(["http://somesite1.onion","http://somesite2.onion"])

    for idx in d_src["source"]:
        for k,v in idx.items():
            print(f"{k}: {v}\n")

                # OR

    for idx in d_r["results"]:
        print(f"Cite: {idx['cite']}")
        print(f"Link: {idx['url']}")
        print(f"Topic: {idx['title']}")
        print(f"Snippet: {idx['snippet']}")
        print(f"Date: {idx['ts']}")
asyncio.run(run())

    # Example keys: search/dark_search/multi_fetch => "results"
    # fetch_source => "source"
    # fetch_context => "content"
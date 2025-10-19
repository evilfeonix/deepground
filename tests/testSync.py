# tests/testSync.py
from deepground.core import Grounder

g = Grounder()
r = g.search("naija latest tech news")                          
ctx = g.fetch_context("https://example.com/article")
src = g.fetch_source("https://example.com/file.txt")

g_tor = Grounder(use_tor=True)
d_r = g_tor.dark_search("proxies combo list")
d_ctx = g_tor.fetch_context("http://tamazoncmlw2ohkbsmqxnotudejdd4befrasxuigzzjumqu3zba535yd.onion")
d_src = g_tor.fetch_source("http://tamazoncmlw2ohkbsmqxnotudejdd4befrasxuigzzjumqu3zba535yd.onion")

# Feed the results straightly to your llm agent
# But for human readability! dev will need to extract and format the original results


g = Grounder()
r = g.search("naija latest tech news")     
for idx in r["results"]:
    for k,v in idx.items():
        print(f"{k}: {v}\n")

            # OR

for idx in r["results"]:
    print(f"Link: {idx['url']}")
    print(f"Topic: {idx['title']}")
    print(f"Snippet: {idx['snippet']}")

# Example keys: search/dark_search => "results"
    # fetch_source => "source"
    # fetch_context => "content"

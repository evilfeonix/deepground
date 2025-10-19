
# tests/testLangchain.py
from deepground.core import GrounderTool

gt = GrounderTool()
r = gt._run("search:naija latest tech news")
ctx = gt._run("fetch_context:https://example.com/article")
src = gt._run("fetch_source:https://example.net/file.txt")
multi_src = gt._run("multi_fetch:https://a.com,https://b.org")

gt_tor = GrounderTool(use_tor=True)
d_r = gt_tor._run("dark_search:naija latest tech news")
d_ctx = gt_tor._run("fetch_context:http://somesite.onion/article")
d_src = gt_tor._run("fetch_source:http://somesite.onion/file.txt")
d_multi_src = gt_tor._run("multi_fetch:http://ss1.onion,http://ss2.onion")

# Freed the results straightly to your llm agent
# But for human readability! dev will need to extract and format the original results
  
for idx in r["results"]:
    for k,v in idx.items():
        print(f"{k}: {v}\n")

            # OR

for idx in r["results"]:
    print(f"Link: {idx['url']}")
    print(f"Topic: {idx['title']}")
    print(f"Snippet: {idx['snippet']}")


    # Example keys: search/dark_search/multi_fetch => "results"
    # fetch_source => "source"
    # fetch_context => "content"

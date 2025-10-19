from deepground.core import Grounder, GrounderAsync, GrounderTool
import asyncio

# Sync usage
g = Grounder()
print(g.search("AI agents", limit=2))
# OUTPUT -> {"results": [{"title": "AI Agents explained", "link": "...", "snippet": "..."}]}

print(g.fetch_context("https://www.python.org"))
# OUTPUT -> {"url": "...", "content": "Python is a programming language... (trimmed)"}

# Async usage
async def test_async():
    async with GrounderAsync() as ga:
        res = await ga.multi_fetch(["https://www.python.org", "https://pypi.org"], context_only=True)
        print(res)

asyncio.run(test_async())
# OUTPUT -> [{"url": "...", "content": "..."}, {"url": "...", "content": "..."}]

# LangChain usage
tool = GrounderTool()
print(tool.run("search:Python web scraping"))
# OUTPUT -> {"results": [{"title": "Web scraping in Python", "link": "..."}]}

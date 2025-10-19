from deepground.core import Grounder

def test_search():
    g = Grounder()
    r = g.search("latest naija news", limit=2)
    assert isinstance(r["results"], list)
    assert "title" in r[0]

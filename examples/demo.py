from deepground.core import Grounder

def main():
 
    g = Grounder()
    print("🌍 Web Search Example")
    res = g.search("latest naija tech news")
    for r in res["results"]:
        print(r)

    print("\n🌑 Darkweb Search Example") 
    g_tor = Grounder(use_tor=True)
    dark_res = g_tor.dark_search("hacking forums")
    for r in dark_res["results"]:
        print(r)

if __name__ == "__main__":
    main()

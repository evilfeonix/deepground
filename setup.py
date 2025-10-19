from setuptools import setup, find_packages

setup( 
    name="deepground",
    version="0.8.2",
    description="Deepground: Async + Sync LLM grounding and web context fetcher (clearnet + darknet)",
    author="Evilfeonix",
    author_email="evilfeonix@proton.me",
    url="https://github.com/evilfeonix/deepground",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "ssl",
        "ddgs",
        "aiohttp",
        "requests",
        "langchain",
        "aiohttp_socks",
        "beautifulsoup4",
        "requests[socks]",
        "typing-extensions",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
    ],
    entry_points={
        "console_scripts": [
            "deepground=deepground.run:main",
        ],
    },
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)


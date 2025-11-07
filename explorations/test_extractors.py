"""
Comprehensive test of web extraction libraries for LLM-driven data pipelines.

Tests multiple libraries against various article types to evaluate:
- Conversion quality
- Performance
- Error handling
- Content cleanliness for LLM consumption
"""

import time
from typing import Any

# Test URLs covering different article types
TEST_URLS = [
    # Technical blog post with code blocks
    "https://simonwillison.net/2024/Oct/29/prompts-dot-js/",
    # Long-form article
    "https://www.anthropic.com/research/building-effective-agents",
    # News article
    "https://www.nytimes.com/2024/01/15/technology/ai-chatgpt-openai.html",
    # Documentation page
    "https://python.langchain.com/docs/introduction/",
]


def test_markitdown() -> dict[str, Any]:
    """Test Microsoft's markitdown library."""
    try:
        from markitdown import MarkItDown

        results = {
            "library": "markitdown",
            "version": None,
            "tests": [],
            "error": None,
        }

        md = MarkItDown()

        for url in TEST_URLS:
            start = time.time()
            try:
                result = md.convert(url)
                elapsed = time.time() - start

                results["tests"].append({
                    "url": url,
                    "success": True,
                    "time_seconds": elapsed,
                    "content_length": len(result.text_content),
                    "sample": result.text_content[:500],
                })
            except Exception as e:
                results["tests"].append({
                    "url": url,
                    "success": False,
                    "error": str(e),
                })

        return results

    except ImportError as e:
        return {
            "library": "markitdown",
            "error": f"Import failed: {e}",
            "tests": [],
        }


def test_trafilatura() -> dict[str, Any]:
    """Test trafilatura library."""
    try:
        import trafilatura

        results = {
            "library": "trafilatura",
            "version": trafilatura.__version__,
            "tests": [],
            "error": None,
        }

        for url in TEST_URLS:
            start = time.time()
            try:
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    # Extract with markdown output
                    content = trafilatura.extract(
                        downloaded,
                        output_format="markdown",
                        include_links=True,
                        include_images=True,
                    )
                    elapsed = time.time() - start

                    results["tests"].append({
                        "url": url,
                        "success": content is not None,
                        "time_seconds": elapsed,
                        "content_length": len(content) if content else 0,
                        "sample": content[:500] if content else "",
                    })
                else:
                    results["tests"].append({
                        "url": url,
                        "success": False,
                        "error": "Failed to download",
                    })
            except Exception as e:
                results["tests"].append({
                    "url": url,
                    "success": False,
                    "error": str(e),
                })

        return results

    except ImportError as e:
        return {
            "library": "trafilatura",
            "error": f"Import failed: {e}",
            "tests": [],
        }


def test_html2text() -> dict[str, Any]:
    """Test html2text library."""
    try:
        import html2text
        import requests

        results = {
            "library": "html2text",
            "version": html2text.__version__,
            "tests": [],
            "error": None,
        }

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # Don't wrap text

        for url in TEST_URLS:
            start = time.time()
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                content = h.handle(response.text)
                elapsed = time.time() - start

                results["tests"].append({
                    "url": url,
                    "success": True,
                    "time_seconds": elapsed,
                    "content_length": len(content),
                    "sample": content[:500],
                })
            except Exception as e:
                results["tests"].append({
                    "url": url,
                    "success": False,
                    "error": str(e),
                })

        return results

    except ImportError as e:
        return {
            "library": "html2text",
            "error": f"Import failed: {e}",
            "tests": [],
        }


def test_newspaper4k() -> dict[str, Any]:
    """Test newspaper4k library."""
    try:
        import newspaper

        results = {
            "library": "newspaper4k",
            "version": newspaper.__version__,
            "tests": [],
            "error": None,
        }

        for url in TEST_URLS:
            start = time.time()
            try:
                article = newspaper.Article(url)
                article.download()
                article.parse()
                elapsed = time.time() - start

                results["tests"].append({
                    "url": url,
                    "success": True,
                    "time_seconds": elapsed,
                    "content_length": len(article.text),
                    "sample": article.text[:500],
                    "metadata": {
                        "title": article.title,
                        "authors": article.authors,
                        "publish_date": str(article.publish_date) if article.publish_date else None,
                    },
                })
            except Exception as e:
                results["tests"].append({
                    "url": url,
                    "success": False,
                    "error": str(e),
                })

        return results

    except ImportError as e:
        return {
            "library": "newspaper4k",
            "error": f"Import failed: {e}",
            "tests": [],
        }


def test_readability() -> dict[str, Any]:
    """Test readability-lxml library."""
    try:
        from readability import Document
        import requests
        import html2text

        results = {
            "library": "readability-lxml",
            "version": None,
            "tests": [],
            "error": None,
        }

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0

        for url in TEST_URLS:
            start = time.time()
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                doc = Document(response.content)
                # Convert cleaned HTML to markdown
                content = h.handle(doc.summary())
                elapsed = time.time() - start

                results["tests"].append({
                    "url": url,
                    "success": True,
                    "time_seconds": elapsed,
                    "content_length": len(content),
                    "sample": content[:500],
                    "title": doc.title(),
                })
            except Exception as e:
                results["tests"].append({
                    "url": url,
                    "success": False,
                    "error": str(e),
                })

        return results

    except ImportError as e:
        return {
            "library": "readability-lxml",
            "error": f"Import failed: {e}",
            "tests": [],
        }


def test_jina_reader() -> dict[str, Any]:
    """Test Jina AI Reader via API."""
    try:
        import requests

        results = {
            "library": "jina-reader",
            "version": "API",
            "tests": [],
            "error": None,
        }

        for url in TEST_URLS[:2]:  # Limit to avoid API abuse
            start = time.time()
            try:
                jina_url = f"https://r.jina.ai/{url}"
                response = requests.get(jina_url, timeout=30)
                response.raise_for_status()
                content = response.text
                elapsed = time.time() - start

                results["tests"].append({
                    "url": url,
                    "success": True,
                    "time_seconds": elapsed,
                    "content_length": len(content),
                    "sample": content[:500],
                })
            except Exception as e:
                results["tests"].append({
                    "url": url,
                    "success": False,
                    "error": str(e),
                })

        return results

    except Exception as e:
        return {
            "library": "jina-reader",
            "error": f"Test failed: {e}",
            "tests": [],
        }


def main() -> None:
    """Run all tests and print results."""
    print("=" * 80)
    print("Web Extraction Library Evaluation")
    print("=" * 80)
    print()

    tests = [
        test_markitdown,
        test_trafilatura,
        test_html2text,
        test_newspaper4k,
        test_readability,
        test_jina_reader,
    ]

    all_results = []

    for test_func in tests:
        print(f"Testing {test_func.__name__.replace('test_', '')}...")
        result = test_func()
        all_results.append(result)

        if result.get("error"):
            print(f"  ERROR: {result['error']}")
        else:
            success_count = sum(1 for t in result["tests"] if t.get("success"))
            total_count = len(result["tests"])
            print(f"  Results: {success_count}/{total_count} successful")

            if result["tests"]:
                avg_time = sum(
                    t.get("time_seconds", 0)
                    for t in result["tests"]
                    if t.get("success")
                ) / max(success_count, 1)
                print(f"  Average time: {avg_time:.2f}s")

        print()

    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    for result in all_results:
        library = result["library"]
        if result.get("error"):
            print(f"{library}: FAILED - {result['error']}")
        else:
            success = sum(1 for t in result["tests"] if t.get("success"))
            total = len(result["tests"])
            print(f"{library}: {success}/{total} tests passed")

    print()

    # Save detailed results
    import json
    output_file = "/Users/fredbliss/workspace/structure-it/explorations/extraction_test_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()

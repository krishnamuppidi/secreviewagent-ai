from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE_URL = "https://krishnamuppidi.github.io/secreviewagent-ai/"
MEASUREMENT_ID = "G-9C5B48SR3B"


def public_pages() -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(SITE.rglob("index.html")):
        relative = path.relative_to(SITE).as_posix()
        route = relative.removesuffix("index.html")
        pages[relative] = urljoin(BASE_URL, route)
    return pages


class MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._hidden_depth = 0
        self.meta: dict[str, str] = {}
        self.links: list[dict[str, str]] = []
        self.scripts: list[str] = []
        self.json_ld: list[str] = []
        self.visible_text: list[str] = []
        self._json_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style"}:
            self._hidden_depth += 1
        if tag == "meta":
            key = attributes.get("name") or attributes.get("property")
            if key:
                self.meta[key] = attributes.get("content", "")
        if tag == "link":
            self.links.append(attributes)
        if tag == "script":
            if attributes.get("src"):
                self.scripts.append(attributes["src"])
            if attributes.get("type") == "application/ld+json":
                self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._json_parts is not None:
            self.json_ld.append("".join(self._json_parts))
            self._json_parts = None
        if tag in {"script", "style"}:
            self._hidden_depth = max(0, self._hidden_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._json_parts is not None:
            self._json_parts.append(data)
        elif not self._hidden_depth and data.strip():
            self.visible_text.append(data.strip())

    def link(self, rel: str, type_: str = "") -> str:
        for attributes in self.links:
            if rel in attributes.get("rel", "").split() and (
                not type_ or attributes.get("type") == type_
            ):
                return attributes.get("href", "")
        return ""


def parse(path: Path) -> MetadataParser:
    parser = MetadataParser()
    parser.feed(path.read_text())
    return parser


def test_every_public_page_has_unique_metadata_and_structured_data() -> None:
    titles: set[str] = set()
    descriptions: set[str] = set()
    assert len(public_pages()) >= 12
    for relative, canonical in public_pages().items():
        parser = parse(SITE / relative)
        assert parser.title and parser.title not in titles
        titles.add(parser.title)
        description = parser.meta.get("description", "")
        assert 80 <= len(description) <= 180, relative
        assert description not in descriptions
        descriptions.add(description)
        assert parser.meta["robots"] == "index, follow, max-image-preview:large"
        assert parser.link("canonical") == canonical
        assert parser.meta["og:url"] == canonical
        assert parser.meta["og:image"] == f"{BASE_URL}assets/secreviewagent-social-preview.png"
        assert parser.meta["twitter:card"] == "summary_large_image"
        assert len(parser.json_ld) == 1
        assert json.loads(parser.json_ld[0])["@context"] == "https://schema.org"


def test_every_public_page_is_substantial_and_machine_readable() -> None:
    for relative in public_pages():
        path = SITE / relative
        parser = parse(path)
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", " ".join(parser.visible_text))
        assert len(words) >= 250, (relative, len(words))
        markdown = path.with_name("index.md")
        assert markdown.is_file()
        assert markdown.read_text().startswith("# ")
        assert "Canonical URL:" in markdown.read_text()
        assert parser.link("alternate", "text/markdown") == "index.md"


def test_consent_gated_analytics_is_on_every_page() -> None:
    analytics = (SITE / "analytics.js").read_text()
    assert f'const MEASUREMENT_ID = "{MEASUREMENT_ID}"' in analytics
    assert 'storedChoice() !== "granted"' in analytics
    assert 'ad_storage: "denied"' in analytics
    assert "allow_google_signals: false" in analytics
    assert "url.search" not in (SITE / "app.js").read_text()
    assert "link.href" not in (SITE / "app.js").read_text()
    for relative in public_pages():
        html = (SITE / relative).read_text()
        parser = parse(SITE / relative)
        depth = len(Path(relative).parts) - 1
        expected = f"{'../' * depth}analytics.js"
        assert expected in parser.scripts
        assert 'id="analytics-consent"' in html
        assert 'id="analytics-preferences"' in html
        assert 'data-analytics-choice="granted"' in html
        assert 'data-analytics-choice="denied"' in html


def test_sitemap_robots_and_machine_discovery_match_pages() -> None:
    root = ET.parse(SITE / "sitemap.xml").getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in root.findall("s:url/s:loc", ns)}
    expected_urls = set(public_pages().values())
    assert sitemap_urls == expected_urls
    assert set((SITE / "sitemap.txt").read_text().splitlines()) == expected_urls
    robots = (SITE / "robots.txt").read_text()
    assert f"Sitemap: {BASE_URL}sitemap.xml" in robots
    for crawler in ("OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "PerplexityBot"):
        assert f"User-agent: {crawler}\nAllow: /" in robots
    llms = (SITE / "llms.txt").read_text()
    assert "Claim boundary:" in llms
    for url in expected_urls:
        assert url in llms or url in (SITE / "llms-full.txt").read_text()


def test_claim_boundaries_and_supported_scope_are_explicit() -> None:
    home = (SITE / "index.html").read_text()
    use_cases = (SITE / "use-cases/index.html").read_text()
    research = (SITE / "research/index.html").read_text()
    assert "not universal production guarantees" in home
    assert "Roadmap integrations, clearly labeled" in use_cases
    assert "not presented as current parser support" in use_cases
    assert "accepted and presented at ICUFN 2026" in research
    assert "Human review remains necessary" in research


def test_public_assets_exist() -> None:
    for relative in (
        "favicon.svg",
        "assets/secreviewagent-social-preview.png",
        "assets/secreviewagent-icufn-2026-paper.pdf",
        "analytics.js",
        "app.js",
        "styles.css",
    ):
        assert (SITE / relative).is_file(), relative

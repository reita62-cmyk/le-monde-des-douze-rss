
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

URL = "https://www.dofus.com/fr/rss/news.xml"
OUTPUT = Path("dofus-news.json")

request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "LeMondeDesDouze-RSS/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml",
    },
)

try:
    with urllib.request.urlopen(request, timeout=20) as response:
        status = response.status
        content = response.read(2_000_001)

    print(f"HTTP : {status}")
    print(f"Octets recus : {len(content)}")

    if status != 200 or not content or len(content) > 2_000_000:
        raise RuntimeError("Flux officiel indisponible")

    root = ET.fromstring(content)
    articles = []

    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        date = (item.findtext("pubDate") or "").strip()

        parsed = urlparse(link)

        if (
            title
            and parsed.scheme == "https"
            and (
                parsed.hostname == "dofus.com"
                or (parsed.hostname or "").endswith(".dofus.com")
            )
        ):
            articles.append({
                "title": title,
                "url": link,
                "date": date,
            })

        if len(articles) == 5:
            break

    if not articles:
        raise RuntimeError("Aucun article officiel valide")

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": articles,
    }

    OUTPUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Succes : {len(articles)} articles recuperes")

except Exception as error:
    print(f"ECHEC : {error}")
    raise SystemExit(1)

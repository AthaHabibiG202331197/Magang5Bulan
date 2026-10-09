import os
import re 
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


# =========================================================
# CONFIG
# =========================================================

BASE_URL = "https://katadata.co.id"
CHANNEL_URL = f"{BASE_URL}/digital" 

OUTPUT_FILE = "data/raw/katadata_enterprise_raw.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    )
}

MAX_PAGES = 5
MAX_ARTICLES = 50 

STRONG_ENTERPRISE_KEYWORDS = [
    "erp",
    "sap",
    "oracle",
    "netsuite",
    "crm",
    "hris",
    "hcm",
    "saas",
    "enterprise software",
    "enterprise application",
    "business software",
    "supply chain management",
    "scm",
] 

CONTEXT_KEYWORDS = [
    "perusahaan",
    "korporasi",
    "enterprise",
    "bisnis",
    "organisasi",
    "karyawan",
    "operasional",
    "proses bisnis",
    "manajemen",
] 


# =========================================================
# HELPER
# =========================================================

def normalize_text(text):
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def is_enterprise_software(title, content):
    """
    Menentukan apakah artikel benar-benar membahas
    Enterprise Software.
    """

    text = f"{title} {content}".lower()

    strong_keywords = [
        "erp",
        "sap",
        "oracle",
        "netsuite",
        "crm",
        "hris",
        "hcm",
        "saas",
        "enterprise software",
        "enterprise application",
        "business software",
        "supply chain management",
        "supply chain software",
        "enterprise resource planning",
        "customer relationship management",
        "human resource information system",
    ]

    matched = []

    for keyword in strong_keywords:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, text):
            matched.append(keyword)

    if not matched:
        return False 

    # Exclude topik yang bukan Enterprise Software
    exclude_keywords = [
        "data center",
        "pusat data",
        "ram",
        "smartphone",
        "ponsel",
        "gadget", 
        "perang",
        "senjata",
        "judi online",
        "judol",
        "kecerdasan buatan",
        "artificial intelligence",
        "generative ai",
        "gemini",
        "grok", 
        "chatgpt",
    ]

    title_lower = title.lower()

    if any(
        keyword in title_lower 
        for keyword in exclude_keywords
    ):
        return False

    return True

    # ---------------------------------------------
    # EXCLUDE topik yang bukan Enterprise Software
    # ---------------------------------------------

    exclude_keywords = [
        "data center",
        "pusat data",
        "ram",
        "smartphone", 
        "ponsel",
        "gadget",
        "perang",
        "senjata",
        "judi online",
        "judol",
        "kecerdasan buatan",
        "artificial intelligence",
        "generative ai",
        "gemini",
        "grok",
        "chatgpt",
    ]

    # Jika artikel hanya membahas topik exclude,
    # jangan masukkan.
    title_lower = title.lower()

    if any(
        keyword in title_lower
        for keyword in exclude_keywords
    ):
        return False

    return True 


# =========================================================
# GET ARTICLE URLS
# =========================================================

def get_article_urls(session):
    print("\nDiscovery Enterprise Software articles...")

    article_urls = [
        "https://katadata.co.id/digital/teknologi/6a5de03439215/cegah-email-spam-dengan-mengelola-database-yang-baik",
        "https://katadata.co.id/digital/teknologi/698eca6d2f5fc/alternatif-sunfish-hris-untuk-perusahaan-enterprise-di-indonesia",
        "https://katadata.co.id/digital/teknologi/69c38dc055568/alasan-bisnis-modern-beralih-ke-saas-ecosystem",
        "https://katadata.co.id/digital/teknologi/654256e01248c/ibm-akuisisi-perusahaan-teknologi-erp-dan-cloud-di-indonesia",
        "https://katadata.co.id/digital/teknologi/5e9a51a81c009/airasia-adopsi-komputasi-awan-milik-oracle",
        "https://katadata.co.id/digital/teknologi/6996e24422b61/7-rekomendasi-aplikasi-procurement-terbaik-untuk-perusahaan-enterprise",
        "https://katadata.co.id/digital/teknologi/625e36c388733/berbisnis-di-media-sosial-lebih-mudah-dengan-whatsapp-api-qontak",
        "https://katadata.co.id/digital/teknologi/62345cb9893d2/whatsapp-api-qontak-tawarkan-solusi-berbisnis-di-era-digital",
        "https://katadata.co.id/digital/teknologi/64080d18b112a/ini-teknologi-yang-masif-diadopsi-perusahaan-di-indonesia",
        "https://katadata.co.id/digital/teknologi/6527acd34e6fe/cerita-startup-tanpa-investor-tapi-sudah-untung",
    ]

    # Deduplicate
    article_urls = list(dict.fromkeys(article_urls))

    print(f"TOTAL DISCOVERED URL: {len(article_urls)}")

    for i, url in enumerate(article_urls, 1):
        print(f"{i}. {url}")

    return article_urls 


# =========================================================
# SCRAPE ARTICLE
# =========================================================

def scrape_article(session, url):

    response = session.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    if response.status_code != 200:
        print(
            f"[SKIP] HTTP {response.status_code}: {url}"
        )
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title = ""

    meta_title = soup.find(
        "meta",
        property="og:title"
    )

    if meta_title:
        title = meta_title.get("content", "")

    if not title and soup.title:
        title = soup.title.get_text(" ", strip=True)

    title = normalize_text(title)

    # -----------------------------------------------------
    # PUBLISHED AT
    # -----------------------------------------------------

    published_at = None

    meta_date = soup.find(
        "meta",
        property="article:published_time"
    )

    if meta_date:
        published_at = meta_date.get("content")

    # -----------------------------------------------------
    # CONTENT
    # -----------------------------------------------------

    content = ""

    content_container = soup.select_one(
        "div.detail-body.mb-4"
    )

    if content_container:

        paragraphs = content_container.find_all("p")

        content = " ".join(
            normalize_text(p.get_text(" ", strip=True))
            for p in paragraphs
        )

    content = normalize_text(content)

    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    relevant = is_enterprise_software(
        title,
        content
    )

    scraped_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return {
        "title": title,
        "url": url,
        "published_at": published_at,
        "channel": "Teknologi",
        "source": "Katadata",
        "content": content,
        "is_enterprise_software": relevant,
        "scraped_at": scraped_at,
    }


# =========================================================
# MAIN
# =========================================================

def main():

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    session = requests.Session()

    article_urls = get_article_urls(session)

    results = []

    for i, url in enumerate(article_urls, start=1):

        print(
            f"\n[{i}/{len(article_urls)}] "
            f"Scraping article..."
        )

        try:

            article = scrape_article(
                session,
                url
            )

            if article:

                print(
                    "Title:",
                    article["title"][:100]
                )

                print(
                    "Published:",
                    article["published_at"]
                )

                print(
                    "Content length:",
                    len(article["content"])
                )

                print(
                    "Enterprise Software:",
                    article["is_enterprise_software"]
                )

                results.append(article)

        except Exception as e:

            print(
                f"[ERROR] {url}"
            )

            print(e)

        time.sleep(1)

    # -----------------------------------------------------
    # DATAFRAME
    # -----------------------------------------------------

    df = pd.DataFrame(results)

    if df.empty:

        print("\nTidak ada data berhasil diambil.")

        return

    # Deduplicate
    df = df.drop_duplicates(
        subset=["url"]
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("SCRAPING SELESAI")
    print("=" * 60)

    print("Total articles:", len(df))

    print(
        "Enterprise Software:",
        df["is_enterprise_software"].sum()
    )

    print(
        "Output:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main() 
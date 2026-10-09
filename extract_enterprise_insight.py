import os
import re
import pandas as pd


INPUT_FILE = "data/processed/katadata_enterprise_filtered.csv"
OUTPUT_FILE = "data/processed/katadata_enterprise_insight.csv"


def normalize_text(text):
    if pd.isna(text):
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()


def detect_event_type(title, content):
    title_text = str(title).lower()
    text = f"{title} {content}".lower()

    # Prioritaskan sinyal dari judul
    if any(k in title_text for k in [
        "rekomendasi",
        "alternatif",
        "pilihan",
        "memilih"
    ]):
        return "Product / Solution Evaluation"

    if any(k in title_text for k in [
        "mengakuisisi",
        "akuisisi",
        "acquisition"
    ]):
        return "Acquisition"

    if any(k in title_text for k in [
        "beralih",
        "pergeseran",
        "meningkat",
        "pertumbuhan",
        "tren"
    ]):
        return "Market / Technology Trend"

    if any(k in text for k in [
        "mengakuisisi",
        "akuisisi",
        "acquisition"
    ]):
        return "Acquisition"

    if any(k in text for k in [
        "mengadopsi",
        "adopsi",
        "menggunakan",
        "digunakan",
        "implementasi",
        "implementasikan"
    ]):
        return "Adoption / Implementation"

    if any(k in text for k in [
        "otomatisasi",
        "automasi",
        "mengotomatisasi"
    ]):
        return "Business Process Automation"

    if any(k in text for k in [
        "beralih",
        "pergeseran",
        "meningkat",
        "pertumbuhan",
        "tren"
    ]):
        return "Market / Technology Trend"

    return "Enterprise Software Activity" 


def detect_technology(title, content, subtopic):
    text = f"{title} {content}".lower()

    technologies = []

    technology_keywords = {
        "SAP": ["sap", "successfactors", "sap ariba"],
        "Oracle": ["oracle", "oracle erp", "oracle hcm"],
        "Zoho CRM": ["zoho crm"],
        "Qontak": ["qontak"],
        "Workday": ["workday"],
        "SunFish HR": ["sunfish"],
        "Mekari": ["mekari", "talenta", "expense"],
        "WhatsApp Business API": ["whatsapp api", "whatsapp business api"],
        "SaaS": ["saas", "software as a service"],
        "Cloud": ["cloud", "cloud-based"],
        "RPA": ["robotic process automation", "rpa"]
    }

    for technology, keywords in technology_keywords.items():
        for keyword in keywords:
            if re.search(
                rf"\b{re.escape(keyword)}\b",
                text,
                re.IGNORECASE
            ):
                technologies.append(technology)
                break

    # Fallback berdasarkan subtopic
    if not technologies:
        technologies.append(subtopic)

    # Deduplicate
    technologies = list(dict.fromkeys(technologies))

    return ", ".join(technologies)


def detect_industry(title, content, subtopic):
    title_text = str(title).lower()
    text = f"{title} {content}".lower()

    # Industri yang eksplisit dari judul
    if any(k in title_text for k in [
        "airasia",
        "maskapai",
        "penerbangan",
        "airline",
        "travel"
    ]):
        return "Travel / Aviation"

    if subtopic == "HRIS / HCM":
        return "Human Resources"

    # Startup/software yang memang menjadi objek utama
    if "startup" in title_text and any(k in text for k in [
        "software",
        "saas",
        "erp"
    ]):
        return "Technology / Software"

    # Untuk ERP, CRM, SaaS dan Procurement,
    # konteks default-nya adalah enterprise umum.
    return "General Enterprise" 


def detect_business_action(title, content, event_type):
    text = f"{title} {content}".lower()

    if any(k in text for k in [
        "mengakuisisi",
        "akuisisi"
    ]):
        return "Corporate Acquisition"

    if any(k in text for k in [
        "mengadopsi",
        "menggunakan",
        "implementasi"
    ]):
        return "Software Adoption"

    if any(k in text for k in [
        "otomatisasi",
        "automasi",
        "mengotomatisasi"
    ]):
        return "Process Automation"

    if any(k in text for k in [
        "rekomendasi",
        "alternatif",
        "memilih"
    ]):
        return "Software Evaluation"

    if event_type == "Market / Technology Trend":
        return "Technology Investment / Adoption"

    return "Business Process Improvement"


def detect_impact(title, content):
    text = f"{title} {content}".lower()

    impacts = []

    impact_keywords = {
        "Operational Efficiency": [
            "efisiensi",
            "meningkatkan produktivitas",
            "menyederhanakan operasi",
            "operasional lebih efisien"
        ],

        "Cost Reduction": [
            "mengurangi biaya",
            "mengurangi biaya operasional",
            "hemat biaya"
        ],

        "Process Automation": [
            "otomatisasi",
            "automasi",
            "mengotomatisasi"
        ],

        "Data Integration": [
            "integrasi data",
            "terintegrasi",
            "data tersentralisasi"
        ],

        "Decision Support": [
            "pengambilan keputusan",
            "keputusan berbasis data",
            "analitik"
        ],

        "Customer Experience": [
            "customer experience",
            "layanan pelanggan",
            "pelanggan"
        ],

        "Business Scalability": [
            "skalabilitas",
            "scalable",
            "pertumbuhan perusahaan"
        ]
    }

    for impact, keywords in impact_keywords.items():
        for keyword in keywords:
            if keyword in text:
                impacts.append(impact)
                break

    if not impacts:
        return "Business Process Improvement"

    return ", ".join(dict.fromkeys(impacts[:3]))


def create_summary(row):
    title = normalize_text(row["title"])
    subtopic = row["subtopic"]
    event_type = row["event_type"]
    technology = row["technology"]
    action = row["business_action"]
    impact = row["impact"]

    return (
        f"Artikel membahas {subtopic} dalam konteks enterprise. "
        f"Fokus utama adalah {event_type.lower()} dengan teknologi "
        f"{technology}. Dari sisi bisnis, hal ini berkaitan dengan "
        f"{action.lower()} dan berpotensi memberikan dampak pada "
        f"{impact.lower()}."
    )


def main():

    print("=" * 60)
    print("INSIGHT EXTRACTION - KATADATA ENTERPRISE SOFTWARE")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File tidak ditemukan: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"Input dataset : {len(df)} rows")

    df["title"] = df["title"].apply(normalize_text)
    df["content"] = df["content"].apply(normalize_text)

    # Identitas artikel
    df["article_id"] = (
        df["url"]
        .astype(str)
        .str.rstrip("/")
        .str.split("/")
        .str[-2]
    )

    df["topic"] = "Enterprise Software"

    # Insight extraction
    df["event_type"] = df.apply(
        lambda row: detect_event_type(
            row["title"],
            row["content"]
        ),
        axis=1
    )

    df["technology"] = df.apply(
        lambda row: detect_technology(
            row["title"],
            row["content"],
            row["subtopic"]
        ),
        axis=1
    )

    df["industry"] = df.apply(
        lambda row: detect_industry(
            row["title"],
            row["content"],
            row["subtopic"]
        ),
        axis=1
    ) 

    df["business_action"] = df.apply(
        lambda row: detect_business_action(
            row["title"],
            row["content"],
            row["event_type"]
        ),
        axis=1
    )

    df["impact"] = df.apply(
        lambda row: detect_impact(
            row["title"],
            row["content"]
        ),
        axis=1
    )

    df["insight_summary"] = df.apply(
        create_summary,
        axis=1
    )

    # Pastikan content status
    if "content_status" not in df.columns:
        df["content_status"] = df["content"].apply(
            lambda x: "SUCCESS"
            if len(str(x).strip()) > 100
            else "EMPTY"
        )

    # Kolom final
    final_columns = [
        "article_id",
        "title",
        "url",
        "published_at",
        "channel",
        "source",
        "topic",
        "subtopic",
        "event_type",
        "technology",
        "industry",
        "business_action",
        "impact",
        "insight_summary",
        "content_status",
        "scraped_at"
    ]

    # Hanya ambil kolom yang tersedia
    final_columns = [
        col for col in final_columns
        if col in df.columns
    ]

    df_final = df[final_columns].copy()

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    df_final.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("INSIGHT EXTRACTION SELESAI")
    print("-" * 60)
    print(f"Total articles : {len(df_final)}")
    print(f"Output         : {OUTPUT_FILE}")

    print()
    print("Subtopic:")
    print(df_final["subtopic"].value_counts().to_string())

    print()
    print("Event Type:")
    print(df_final["event_type"].value_counts().to_string())

    print()
    print("Industry:")
    print(df_final["industry"].value_counts().to_string())

    print()
    print("Business Action:")
    print(df_final["business_action"].value_counts().to_string())

    print()
    print("Preview:")
    print(
        df_final[
            [
                "title",
                "subtopic",
                "event_type",
                "technology",
                "industry",
                "business_action",
                "impact"
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main() 
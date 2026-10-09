import os
import re
import pandas as pd


INPUT_FILE = "data/processed/katadata_enterprise_clean.csv"

OUTPUT_ALL = "data/processed/katadata_enterprise_filtered_all_classified.csv"
OUTPUT_FILTERED = "data/processed/katadata_enterprise_filtered.csv"


SUBTOPIC_KEYWORDS = {
    "ERP": [
        "erp",
        "enterprise resource planning",
        "sap",
        "oracle erp",
        "oracle cloud",
        "dynamics"
    ],

    "CRM": [
        "crm",
        "customer relationship management",
        "zoho crm",
        "salesforce",
        "qontak"
    ],

    "HRIS / HCM": [
        "hris",
        "hcm",
        "human resource information system",
        "human capital management",
        "sap successfactors",
        "oracle hcm",
        "workday",
        "sunfish"
    ],

    "SaaS": [
        "saas",
        "software as a service",
        "saas ecosystem",
        "cloud-based software"
    ],

    "Procurement / SCM": [
        "procurement",
        "supply chain",
        "supply chain management",
        "sap ariba",
        "oracle procurement"
    ],

    "Enterprise Application": [
        "enterprise software",
        "enterprise application",
        "business software",
        "business application"
    ]
}


def find_matches(text, keywords):
    matches = []

    for keyword in keywords:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, text, re.IGNORECASE):
            matches.append(keyword)

    return matches


def classify_article(row):

    title = str(row.get("title", ""))
    content = str(row.get("content", ""))

    title_lower = title.lower()
    text = f"{title} {content}"

    scores = {}
    matches_by_subtopic = {}

    for subtopic, keywords in SUBTOPIC_KEYWORDS.items():

        matches = find_matches(text, keywords)

        if not matches:
            continue

        score = 0

        for keyword in matches:

            # Match di title diberi bobot lebih tinggi
            if re.search(
                rf"\b{re.escape(keyword)}\b",
                title_lower,
                re.IGNORECASE
            ):
                score += 5
            else:
                score += 1

        scores[subtopic] = score
        matches_by_subtopic[subtopic] = matches

    if not scores:
        return {
            "is_relevant": False,
            "subtopic": "Other",
            "matched_keywords": "",
            "filter_reason": "No Enterprise Software subtopic matched"
        }

    # Prioritas jika score sama
    priority = {
        "HRIS / HCM": 6,
        "Procurement / SCM": 5,
        "ERP": 4,
        "CRM": 3,
        "SaaS": 2,
        "Enterprise Application": 1
    }

    selected_subtopic = max(
        scores,
        key=lambda x: (
            scores[x],
            priority.get(x, 0)
        )
    )

    matched = matches_by_subtopic[selected_subtopic]

    return {
        "is_relevant": True,
        "subtopic": selected_subtopic,
        "matched_keywords": ", ".join(matched),
        "filter_reason": f"Matched {selected_subtopic}"
    } 


def main():

    print("=" * 60)
    print("FILTERING KATADATA ENTERPRISE SOFTWARE")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File tidak ditemukan: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"Input dataset : {len(df)} rows")

    results = df.apply(
        classify_article,
        axis=1,
        result_type="expand"
    )

    df = pd.concat(
        [df, results],
        axis=1
    )

    # Simpan semua hasil klasifikasi
    os.makedirs(
        os.path.dirname(OUTPUT_ALL),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_ALL,
        index=False
    )

    # Hanya artikel relevan
    filtered = df[
        df["is_relevant"] == True
    ].copy()

    filtered.to_csv(
        OUTPUT_FILTERED,
        index=False
    )

    print()
    print("FILTERING SELESAI")
    print("-" * 60)

    print(f"Total input       : {len(df)}")
    print(f"Relevan           : {len(filtered)}")
    print(f"Tidak relevan     : {len(df) - len(filtered)}")

    print()
    print("Subtopic Distribution:")
    print(
        filtered["subtopic"]
        .value_counts()
        .to_string()
    )

    print()
    print("Detail Classification:")

    print(
        filtered[
            [
                "title",
                "subtopic",
                "matched_keywords"
            ]
        ].to_string(index=False)
    )

    print()
    print(f"Output all        : {OUTPUT_ALL}")
    print(f"Output filtered   : {OUTPUT_FILTERED}")


if __name__ == "__main__":
    main()                                                                
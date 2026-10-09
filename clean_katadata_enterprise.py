import os
import re
import pandas as pd


INPUT_FILE = "data/raw/katadata_enterprise_raw.csv"
OUTPUT_FILE = "data/processed/katadata_enterprise_clean.csv"


def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # Normalisasi whitespace
    text = re.sub(r"\s+", " ", text)

    # Hapus spasi berlebih
    text = text.strip()

    return text


def main():

    print("=" * 60)
    print("CLEANING KATADATA ENTERPRISE SOFTWARE")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File tidak ditemukan: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"Input dataset : {len(df)} rows")

    # Cleaning title
    if "title" in df.columns:
        df["title"] = df["title"].apply(clean_text)

    # Cleaning content
    if "content" in df.columns:
        df["content"] = df["content"].apply(clean_text)

    # Normalize URL
    if "url" in df.columns:
        df["url"] = df["url"].astype(str).str.strip()

    # Convert published_at
    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(
            df["published_at"],
            errors="coerce"
        )

    # Convert scraped_at
    if "scraped_at" in df.columns:
        df["scraped_at"] = pd.to_datetime(
            df["scraped_at"],
            errors="coerce"
        )

    # Hapus duplicate URL
    before = len(df)

    df = df.drop_duplicates(
        subset=["url"],
        keep="first"
    )

    duplicates_removed = before - len(df)

    # Hapus artikel tanpa URL
    df = df[df["url"].notna()]
    df = df[df["url"].str.strip() != ""]

    # Hapus artikel tanpa title
    df = df[df["title"].notna()]
    df = df[df["title"].str.strip() != ""]

    # Status content
    df["content_status"] = df["content"].apply(
        lambda x: "SUCCESS"
        if isinstance(x, str) and len(x.strip()) > 100
        else "EMPTY"
    )

    # Pastikan hanya kandidat Enterprise Software
    if "is_enterprise_software" in df.columns:
        df["is_enterprise_software"] = (
            df["is_enterprise_software"]
            .astype(str)
            .str.lower()
            .map({
                "true": True,
                "false": False
            })
        )

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("CLEANING SELESAI")
    print("-" * 60)
    print(f"Output              : {OUTPUT_FILE}")
    print(f"Final dataset       : {len(df)} rows")
    print(f"Duplicate dihapus   : {duplicates_removed}")

    if "content_status" in df.columns:
        print()
        print("Content Status:")
        print(df["content_status"].value_counts())

    if "is_enterprise_software" in df.columns:
        print()
        print("Enterprise Software:")
        print(df["is_enterprise_software"].value_counts(dropna=False))


if __name__ == "__main__":
    main() 
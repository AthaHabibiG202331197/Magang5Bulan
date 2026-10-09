import os
import pandas as pd
from sqlalchemy import create_engine, text


INPUT_FILE = "data/processed/katadata_enterprise_insight.csv"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "market_intelligence")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD") 

TABLE_NAME = "sector3_articles"


def main():

    print("=" * 60)
    print("LOAD ENTERPRISE SOFTWARE TO POSTGRESQL")
    print("=" * 60)

    if not DB_PASSWORD:
        print("ERROR: DB_PASSWORD belum diset.")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File tidak ditemukan: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"Input dataset : {len(df)} rows")

    # Pastikan datetime
    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce"
    )

    df["scraped_at"] = pd.to_datetime(
        df["scraped_at"],
        errors="coerce"
    )

    # Pastikan topic
    df["topic"] = "Enterprise Software"

    # Kolom sesuai tabel sector3_articles
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

    df = df[final_columns].copy()

    # SQLAlchemy + psycopg2
    connection_string = (
        f"postgresql+psycopg2://"
        f"{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    ) 

    engine = create_engine(connection_string)

    print(
        f"Connecting to PostgreSQL: "
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    upsert_query = text("""
        INSERT INTO sector3_articles (
            article_id,
            title,
            url,
            published_at,
            channel,
            source,
            topic,
            subtopic,
            event_type,
            technology,
            industry,
            business_action,
            impact,
            insight_summary,
            content_status,
            scraped_at
        )
        VALUES (
            :article_id,
            :title,
            :url,
            :published_at,
            :channel,
            :source,
            :topic,
            :subtopic,
            :event_type,
            :technology,
            :industry,
            :business_action,
            :impact,
            :insight_summary,
            :content_status,
            :scraped_at
        )
        ON CONFLICT (url)
        DO UPDATE SET
            title = EXCLUDED.title,
            published_at = EXCLUDED.published_at,
            channel = EXCLUDED.channel,
            source = EXCLUDED.source,
            topic = EXCLUDED.topic,
            subtopic = EXCLUDED.subtopic,
            event_type = EXCLUDED.event_type,
            technology = EXCLUDED.technology,
            industry = EXCLUDED.industry,
            business_action = EXCLUDED.business_action,
            impact = EXCLUDED.impact,
            insight_summary = EXCLUDED.insight_summary,
            content_status = EXCLUDED.content_status,
            scraped_at = EXCLUDED.scraped_at;
    """)

    inserted = 0

    with engine.begin() as conn:

        for _, row in df.iterrows():

            conn.execute(
                upsert_query,
                row.to_dict()
            )

            inserted += 1

    print()
    print("DATABASE LOAD SELESAI")
    print("-" * 60)
    print(f"Processed Enterprise Software : {inserted}")

    # Verifikasi
    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (
                        WHERE topic = 'Cyber Security'
                    ) AS cyber_security,
                    COUNT(*) FILTER (
                        WHERE topic = 'Enterprise Software'
                    ) AS enterprise_software
                FROM sector3_articles
            """)
        ).fetchone()

    print()
    print("DATABASE VERIFICATION")
    print("-" * 60)
    print(f"Total articles       : {result.total}")
    print(f"Cyber Security       : {result.cyber_security}")
    print(f"Enterprise Software  : {result.enterprise_software}")


if __name__ == "__main__":
    main() 
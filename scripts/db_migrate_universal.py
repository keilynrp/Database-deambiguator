
import sqlite3
import json

db_path = "backend/data/database.db"

# However, the user states DB path is sql_app.db in root. Let's use that.
db_path = "sql_app.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

try:
    # 1. Create the new table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS universal_entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain VARCHAR DEFAULT 'ecommerce',
        entity_type VARCHAR,
        primary_label VARCHAR,
        secondary_label VARCHAR,
        canonical_id VARCHAR,
        attributes_json TEXT DEFAULT '{}',
        validation_status VARCHAR DEFAULT 'pending',
        normalized_json TEXT,
        enrichment_doi VARCHAR,
        enrichment_citation_count INTEGER DEFAULT 0,
        enrichment_concepts TEXT,
        enrichment_source VARCHAR,
        enrichment_status VARCHAR DEFAULT 'none',
        source VARCHAR DEFAULT 'user'
    );
    ''')

    # 2. Check if raw_entities exists and has data
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw_entities'").fetchone()
    if res:
        # Check rows
        rows = cur.execute("SELECT * FROM raw_entities").fetchall()
        if len(rows) == 0:
            # Empty db, just drop and rename
            cur.execute("DROP TABLE raw_entities")
            cur.execute("ALTER TABLE universal_entities RENAME TO raw_entities")
            print("Swapped empty tables.")
        else:
            print("DB has data, need data migration mapping logic for 50 columns. Not implemented in this basic script yet.")
    else:
        print("raw_entities not found.")
        
    # We must ensure raw_entities has the NEW SCHEMA! (primary_label, domain, attributes_json)
    
    conn.commit()

except Exception as e:
    print(e)
finally:
    conn.close()

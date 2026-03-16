import os
import re

MODELS_PATH = "backend/models.py"

with open(MODELS_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# We want to replace the RawEntity definition in models.py
# Let's find the start and end of RawEntity definition
start_idx = content.find("class RawEntity(Base):")
if start_idx == -1:
    print("Could not find RawEntity in models.py")
    exit(1)

next_class_idx = content.find("class NormalizationRule(Base):", start_idx)

if next_class_idx == -1:
    print("Could not find next class")
    exit(1)

old_def = content[start_idx:next_class_idx]

# Define the new RawEntity class with hybrid properties
new_def = """import json
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy as sa

class UniversalEntity(Base):
    __tablename__ = "raw_entities"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- Universal Paradigm (Phase 8) ---
    domain = Column(String, default="ecommerce", index=True)  # science, healthcare, business, etc.
    entity_type = Column(String, default="product", index=True) # Type classification
    
    primary_label = Column(String, index=True)      # e.g., product_name, paper title
    secondary_label = Column(String)                # e.g., brand, author
    canonical_id = Column(String, index=True)       # e.g., sku, doi, gtin
    
    attributes_json = Column(Text, default="{}")    # Flexible data schema
    
    # Metadata
    validation_status = Column(String, default="pending", index=True)
    normalized_json = Column(Text, nullable=True)   # Keep for harmonization backward compat

    # Scientometric Enrichment Fields
    enrichment_doi = Column(String, nullable=True)
    enrichment_citation_count = Column(Integer, default=0)
    enrichment_concepts = Column(Text, nullable=True) 
    enrichment_source = Column(String, nullable=True)
    enrichment_status = Column(String, default="none", index=True)

    # Data provenance
    source = Column(String, default="user")

    # =========================================================
    # BACKWARD COMPATIBILITY LAYER (e-commerce legacy fields)
    # =========================================================
    
    @hybrid_property
    def entity_name(self): return self.primary_label
    @entity_name.setter
    def entity_name(self, val): self.primary_label = val
    @entity_name.expression
    def entity_name(cls): return cls.primary_label

    @hybrid_property
    def sku(self): return self.canonical_id
    @sku.setter
    def sku(self, val): self.canonical_id = val
    @sku.expression
    def sku(cls): return cls.canonical_id

    # JSON mappings
    def _get_attr(self, key):
        if not self.attributes_json: return None
        return json.loads(self.attributes_json).get(key)

    def _set_attr(self, key, val):
        d = json.loads(self.attributes_json) if self.attributes_json else {}
        d[key] = val
        self.attributes_json = json.dumps(d)

"""

# Add JSON mapped properties
legacy_columns = [
    "classification", "is_decimal_sellable", "control_stock", "status", "taxes",
    "variant", "entity_code_universal_1", "entity_code_universal_2", "entity_code_universal_3",
    "entity_code_universal_4", "brand_lower", "brand_capitalized", "model", "gtin",
    "gtin_reason", "gtin_empty_reason_1", "gtin_empty_reason_2", "gtin_empty_reason_3",
    "gtin_entity_reason", "gtin_reason_lower", "gtin_empty_reason_typo", "equipment",
    "measure", "union_type", "allow_sales_without_stock", "barcode", "branches",
    "creation_date", "variant_status", "entity_key", "unit_of_measure"
]

for col in legacy_columns:
    new_def += f"""
    @hybrid_property
    def {col}(self): return self._get_attr("{col}")
    @{col}.setter
    def {col}(self, val): self._set_attr("{col}", val)
    @{col}.expression
    def {col}(cls): return sa.func.json_extract(cls.attributes_json, '$.{col}')
"""

# Now write back, but wait, RawEntity name!
# We renamed RawEntity to UniversalEntity. But the rest of the code queries `models.RawEntity`.
# So let's alias it at the end.
new_def += "\n# Alias for backward compatibility\nRawEntity = UniversalEntity\n\n"

new_content = content[:start_idx] + new_def + content[next_class_idx:]

with open(MODELS_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Updated {MODELS_PATH}")

# Now we need to create the SQLite migration script that actually updates databse.db
migration = """
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
"""
with open("scripts/db_migrate_universal.py", "w", encoding="utf-8") as f:
    f.write(migration)
print("Migration script created.")

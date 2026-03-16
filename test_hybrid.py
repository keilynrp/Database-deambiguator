import json
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

class UniversalEntity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    primary_label = Column(String)
    attributes_json = Column(Text, default="{}")

    @hybrid_property
    def brand_capitalized(self):
        return self.primary_label
        
    @brand_capitalized.setter
    def brand_capitalized(self, val):
        self.primary_label = val

    @brand_capitalized.expression
    def brand_capitalized(cls):
        return cls.primary_label

    @hybrid_property
    def classification(self):
        return json.loads(self.attributes_json).get("classification") if self.attributes_json else None

    @classification.setter
    def classification(self, val):
        d = json.loads(self.attributes_json) if self.attributes_json else {}
        d["classification"] = val
        self.attributes_json = json.dumps(d)

    @classification.expression
    def classification(cls):
        import sqlalchemy as sa
        return sa.func.json_extract(cls.attributes_json, '$.classification')

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# 1. Create using old keys
e = UniversalEntity(brand_capitalized="Sony", classification="Electronics")
db.add(e)
db.commit()

# 2. Query using old keys
res = db.query(UniversalEntity).filter(UniversalEntity.brand_capitalized == "Sony").first()
print("Found by brand:", res.classification if res else "None")

res2 = db.query(UniversalEntity).filter(UniversalEntity.classification == "Electronics").first()
print("Found by classification:", res2.brand_capitalized if res2 else "None")

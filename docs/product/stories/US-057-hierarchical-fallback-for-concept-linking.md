# US-057 - Hierarchical Fallback for Concept Linking

## 1. User story

Como analista, quiero que cuando un concepto no exista de forma exacta en una KB el sistema pueda enlazarlo a un concepto mas general para conservar valor semantico en vez de degradarlo solo a `NIL`.

## 2. Context

- Epic: `EPIC-004`
- Dependencia recomendada: `US-056`

## 3. Acceptance criteria

- [x] existe fallback opcional a conceptos ancestro o mas generales donde la KB exponga jerarquia usable
- [x] el sistema persiste el tipo de match parcial y la distancia o nivel jerarquico cuando sea posible
- [x] la UI diferencia entre `exact_match`, `partial_ancestor_match` y `NIL`
- [x] el fallback no se aplica ciegamente a autores; queda acotado a tipos de entidad donde la jerarquia tenga sentido
- [x] el sistema mantiene evidencia suficiente para auditoria y revision humana

## 4. Functional notes

- prioridad para `concept`, `topic`, taxonomias institucionales o fuentes jerarquicas
- no se recomienda como heuristica principal para entidades `person`
- debe ser source-aware: solo usarlo donde la KB realmente tenga arbol o grafo semantico estable

## 5. Technical notes

- adapters de authority y metadata de fuentes externas
- `backend/authority/resolver.py`
- `backend/authority/scoring.py`
- `backend/routers/authority.py`
- `backend/models.py`
- `frontend/app/authority/page.tsx`

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 8. Evidence

- fallback: `backend/authority/hierarchical_fallback.py`
- persistence: `AuthorityRecord.hierarchy_distance`, `alembic/versions/c2d3e4f5a6b7_sprint_106_hierarchical_fallback.py`
- endpoints: `POST /authority/resolve`, `POST /authority/resolve/batch`
- UI: `frontend/app/authority/page.tsx`
- tests: `backend/tests/test_sprint106_hierarchical_fallback.py`

## 7. Notes for prioritization

- vale la pena, pero despues de `US-056`
- aporta mas a NIL linking de conceptos que al wedge author-only inicial

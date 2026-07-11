# Empieza aquí

Este zip te deja una carpeta lista para empezar el repo:

```text
supply-chain-decision-twin-agent
```

La idea es que tú tengas la estructura profesional lista y que **Dify haga el trabajo pesado**:

1. Leer documentación con RAG.
2. Consultar SQL operacional.
3. Consultar/escribir SQL memory.
4. Generar recomendaciones.
5. Aplicar validación.
6. Exigir aprobación humana.
7. Mantener límites de claim.

## Orden recomendado

### Paso 1: crear entorno

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Paso 2: crear base SQLite

```bash
python src/create_database.py
```

Esto crea:

```text
data/supply_chain.db
```

con dos capas:

```text
SQL operacional: productos, inventario, escenarios
SQL memory: decisiones, trazas, aprobaciones
```

### Paso 3: correr demo local

```bash
python src/query_stockout_risk.py
```

Esto consulta SKUs con riesgo de stockout y guarda una decisión en memoria.

### Paso 4: correr tests

```bash
pytest
```

### Paso 5: configurar Dify

En Dify:

1. Crea una app tipo Workflow o Agent.
2. Crea Knowledge Base.
3. Sube estos archivos:
   - README.md
   - docs/KPI_DICTIONARY.md
   - docs/SEMANTIC_CONTRACT.md
   - docs/CLAIM_BOUNDARIES.md
   - docs/HUMAN_APPROVAL_CHECKPOINT.md
   - docs/VALIDATION_LIFECYCLE.md
4. Copia el prompt de:
   - dify/system_prompt.md
5. Usa el diseño de flujo de:
   - dify/workflow_design.md
6. Conecta SQL:
   - si Dify no acepta SQLite directo, migra las tablas a Postgres.
7. Prueba preguntas de:
   - dify/sample_questions.md

## Pregunta MVP

Prueba en Dify:

```text
Which SKUs are at stockout risk next week and why?
```

La respuesta ideal debe incluir:

```text
Business decision
Governed KPI
SQL evidence
Validation status
Human approval requirement
Claim boundary
```

## Regla de oro

No digas que esto es producción.

Di:

```text
Synthetic/local decision-support lab.
Human-validated AI workflow.
Governed KPI decision-support pattern.
```

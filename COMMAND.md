# Project commands

## Every session
cd ~/Desktop/clinical-intel-platform/clinical-intel-platform
source .venv/bin/activate          # leave: deactivate
docker compose up -d               # start FHIR + MinIO (Docker Desktop must be open)

## Docker
docker compose ps -a               # status
docker compose logs fhir | tail -40
docker compose down                # stop, keep data
docker compose rm -sf fhir         # throw away the FHIR container (fresh DB)

## Python env
python -m pip install -e ".[dev]"  # (re)install deps
python -c "import ingestion, dagster, dbt; print('ok')"

## Data
python scripts/load_fhir.py        # Synthea bundles -> FHIR
# FHIR count:  http://localhost:8080/fhir/Patient?_summary=count
# MinIO UI:    http://localhost:9001  (minioadmin / change-me-please)

## Housekeeping
df -h ~                            # disk space
conda deactivate                   # if (base) appears
python -m pip cache purge          # free pip cache

## Git
git status
git add -A && git commit -m "message"
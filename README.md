# Pytest suite for File DB Manager

## Files
- `conftest.py` — dynamic import fixture for the app module (with `ttkbootstrap` stubs)
- `test_core_logic.py` — tests for non-GUI core logic

## Run
```bash
cd /mnt/data/pytest_file_db_manager
pytest -q
```

If your script path changes, update `SCRIPT_CANDIDATES` in `conftest.py`.

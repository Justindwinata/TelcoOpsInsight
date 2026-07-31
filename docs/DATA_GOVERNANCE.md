# Data Governance

TOI-0002 adds safer local CSV governance for the synthetic dataset.

## CSV Validation

CSV uploads are schema-detected and validated before any persisted import. Invalid files return structured errors and do not replace existing SQLite tables.

## Safe Import

`POST /api/datasets/upload?persist=true` replaces only the table matching the accepted dataset type. Replacement happens after validation passes and is executed in a SQLite transaction. Failed validation does not drop or corrupt the current table.

## Import History

Each upload attempt is recorded in `import_history` with `import_id`, filename, dataset type, timestamp, row counts, status, validation summary, and actor.

Statuses:

- `validated`: valid preview without persistence.
- `imported`: valid persisted replacement.
- `rejected`: invalid upload.

## Limitations

Import history is local SQLite metadata. There is no enterprise audit log, external data catalog, or cloud governance integration in TOI-0002.

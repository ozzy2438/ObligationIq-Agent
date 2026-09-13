# Local Unity Catalog — Phase 2 fallback

Phase 2 is complete for the source-reviewed register using the brief's Section 3 local fallback. This is an actual Unity Catalog OSS service registering an existing external Delta table. It is not a managed Databricks workspace or a cloud evaluation.

## Reproduce

Install Docker and the `register` optional Python dependencies. Materialize the reviewed register first. The pinned image download uses the internet; subsequent catalog operations use only `127.0.0.1:8087`.

```sh
python -m src.register.obligations materialize
python scripts/local_catalog.py start
python scripts/local_catalog.py verify
python scripts/local_catalog.py stop
```

`data/catalog-runtime.json` pins the official Unity Catalog 0.5.0 image by OCI digest. The source tag/commit is a reference for inspecting its API; no image build attestation is claimed. No Azure or Databricks credentials are passed to the container. Existing Databricks CLI authentication was unavailable, and no paid workspace was provisioned.

The service uses a dedicated Docker volume, an explicit loopback port, authorization enabled, a bootstrap administrator, and a read-only mount of the register. Local token copies live in a private ignored directory with mode 0600. Neither tokens nor signing keys are committed. The script refuses a container with the wrong label/image or a nonlocal URL. Stop retains the volume and Delta history. Do not remove either when retaining evidence.

## Observed evidence

[Generated verification](catalog-verification.json) records 32 rows, 35 typed columns, catalog-resolved reads matching the reviewed Delta snapshot, rejection of anonymous catalog access, unchanged repeat registration and persistent table identity across a service restart. All three existing Delta snapshots (0, 1 and 2) remain readable with 32 rows each. The readback compares the full nested column types, not just their top-level names.

The legacy `POST /tables` route returned HTTP 500 in its authorization expression while registering this schema. The documented [UC Delta API](https://unitycatalog.io/blogs/unity-catalog-delta-api/) registered the external table successfully with authorization enabled. Its array schema uses `element-type` and `contains-null`, unlike Delta log JSON. The adapter explicitly translates those two keys. No server patch or disabled authorization was used. An attempted v0.5.1 image pull returned not found; it was not used.

## Exact boundary

Unity Catalog resolves `obligationiq.register.obligations` to the local Delta location. Delta's own log remains authoritative for data versions; reads explicitly select the actual Delta version. The UC Delta REST metadata counter is not treated as the existing external Delta log version. This is metadata registration and resolution, not catalog-managed transactions or enforcement over local files.

The host owner can read/write those files independently of UC. Bootstrap admin access is not a verified multi-user permissions model. Row-level security, automated lineage, storage credential vending, production availability and managed Databricks are unverified. The optional catalog verification deliberately restarts this project's container; it never runs in ordinary offline CI.

Source approval does not establish a customer's legal applicability. State application instruments, effective-date logic, business-day calendars and executable controls belong to the subsequent control implementation gate. No customer compliance result or permission to disconnect follows from this Phase 2 completion.

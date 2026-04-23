# Dokploy REST API Notes

The canonical endpoint reference now lives at
[references/dokploy_api.md](references/dokploy_api.md).

This top-level file stays as a stable compatibility entrypoint for older links
and docs. The maintained reference covers:

- deploy, status, inspect, and runtime log endpoints
- the 404 log fallback through `docker.*` discovery plus `/docker-container-logs`
- common create and update flows for projects, apps, databases, ports, and domains
- schema discovery with `zodError.fieldErrors`

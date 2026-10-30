# Orphaned `preflight.yml` Task Files

The following task files are **not referenced by any role's `main.yml` or any playbook**
(confirmed via repo-wide grep). They appear to predate the current `verify-host.yml` /
`verify-connectivity.yml` / `verify-results.yml` mechanism (see `roles/common/CLAUDE.md`)
and were left behind after that refactor:

- `roles/platform/tasks/preflight.yml`
- `roles/mongodb/tasks/preflight.yml`
- `roles/redis/tasks/preflight.yml`

Each references `ansible_distribution_major_version`-keyed variables (and, in the Redis
case, variables like `redis_repo_url` / `invalid_redis_release` that no longer exist
anywhere else in the codebase), so they would need version-specific updates (e.g. for
RHEL/Rocky 10 support) if ever revived — but since nothing wires them in, those updates
were skipped when adding RHEL/Rocky 10 support (see the `rhel10_support` branch).

The associated templates (`platform.preflight.j2`, `mongodb.preflight.j2`,
`redis.preflight.j2`) are also unused for the same reason.

**Recommendation:** delete all six files (three `preflight.yml` task files + three
`*.preflight.j2` templates) in a dedicated cleanup PR, since the current `verify_*`
playbooks supersede their functionality. Left in place for now to keep the RHEL10 branch
diff focused on OS-version support.

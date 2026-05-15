# Role: selinux

## Purpose

Shared utility role for compiling and installing custom SELinux policy modules (`.te` files). Called by `mongodb`, `redis`, and `gateway` roles via `include_tasks`. Reads `.te` files from the **calling role's** `files/` directory (not this role's own files).

## Entry Point Tasks — main.yml

Entire block is guarded by `ansible_selinux.status == "enabled"`.

1. Find all `*.te` files in `{{ ansible_parent_role_paths | first }}/files/` on the control node (delegated to localhost)
2. Build list of policy files
3. Check which policies are already installed via `semodule -l | grep <name>` (per file)
4. Remove already-installed policies from the list to avoid recompilation
5. For remaining policies:
   a. Create a temp directory on the target node
   b. Copy `.te` files from control node to target temp dir
   c. Compile each: `checkmodule -M -m -o <name>.mod <name>.te`
   d. Package each: `semodule_package -o <name>.pp -m <name>.mod`
   e. Install all: `semodule -i *.pp` (from the temp dir)
   f. Remove temp directory

## configure-context.yml

A second task file in this role. Called by individual component roles (e.g., mongodb, redis) to apply `semanage fcontext` and `restorecon` context labels. The calling role must pass the context rules — this file does not define any rules itself.

## Variables

None defined in this role. It reads `ansible_parent_role_paths` (an Ansible magic variable) to locate the calling role's `files/` directory.

## SELinux Policy Files per Component Role

| Role | Policy Files (in role's `files/`) |
|------|----------------------------------|
| `mongodb` | `itential_mongodb_cgroup_memory.te`, `itential_mongodb_proc_net.te`, `itential_mongodb_sysctl_fs.te`, `itential_mongodb_sysctl_net.te`, `itential_mongodb_var_lib_nfs.te` |
| `redis` | `itential_redis_sentinel.te` |
| `gateway` | (none — gateway calls `configure-selinux.yml` which includes its own inline tasks) |

## Dependencies / Assumptions

- Must be called with `include_tasks` or `import_role` from within a role that has `.te` files in its `files/` directory.
- `ansible_parent_role_paths` is automatically set by Ansible when a role includes another role's tasks. If called incorrectly, the file discovery will fail silently (empty list) or error.
- Requires `checkmodule`, `semodule_package`, and `semodule` to be installed on the target (provided by `policycoreutils` and `checkpolicy` packages from the `os` role).
- The entire role is a no-op when SELinux is disabled or permissive (`ansible_selinux.status != "enabled"`).

## Gotchas

- The idempotency check uses `semodule -l | grep <filename_without_extension>`. If a policy is installed under a different name than the `.te` filename, this check will miss it and attempt to reinstall.
- `semodule -i *.pp` runs from the temp directory using a shell glob — all compiled `.pp` files are installed in one command. Order of installation is not controlled.
- The role uses `changed_when: result.rc == 0` on compile/package steps, which means every run where the policy is not already installed will show as changed, even on re-runs.

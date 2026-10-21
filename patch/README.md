# Patched release builds

Patch base: upstream **3.1.0**, commit `eeef60b22ba24383daf51f3c6c2e5b75bbab6bba`.
Apply with `bash scripts/apply-patches.sh <clean-upstream-checkout>` in this order:

1. `image-compress.patch`: optional outgoing image compression, existing settings retained.
2. `user-experience.patch`: `{{time}}` and streaming Markdown export without embedded images.
3. `workspace-browser.patch`: the existing dual-pane workspace file browser, ported to 3.1.
4. `legacy-migration.patch`: one-time upgrade compatibility for the old fork database.

CI builds an upstream release **plus these patches**, not the fork's root application
source. Strict sequential application is intentional: no fuzzy/reject repairs in CI.
Rebase and test before changing the upstream base. Do not edit only root Kotlin files.

## Official conversation compression

All live compression, model selection, settings, checkpoint rendering and request
context selection use the unmodified upstream implementation. The old target-token
option, custom compression model/prompt, compressed node flags, UI tags and generation
merge helpers have been removed from the live code. No old `PatchedHistory` remains.

Upstream 3.1.0 summarizes the current context with the current chat model. It retains
history and inserts an official checkpoint; there is no keep-recent or target-token
setting. Recompression summarizes the last checkpoint and subsequent messages.

## Upgrade compatibility

The old fork used schema 25/26 for custom `compressed` and `is_summary` columns;
upstream 26 instead added media-creation tables. Never use an unmodified automatic
26→27 migration on that fork database.

The compatibility patch replaces only 24→25, 25→26 and 26→27 with guarded migrations:

- Add the workspace compatibility column if missing (also handles early fork 25).
- Create the official media tables/indices if absent, including when starting at fork 26.
- Add official conversation config, convert old summaries, and rebuild message_node
  without custom columns, matching official schema 27 exactly.
- Continue through upstream's normal 27→28 memory migration and later migrations to
  **official schema 31** (including upstream 30→31 migration). No fork schema bump or destructive fallback is introduced.

Each legacy conversation retains its original nodes, message JSON, selected branches,
IDs, attachments and favorites. Its old summary chunks are joined in a new official
checkpoint inserted after the archived prefix and before retained recent messages.
No model/API call is made. Old summary nodes remain visible as historical records.
After migration only the new checkpoint and following messages reach the model.

Missing/invalid summaries or interleaved archived/live nodes abort the migration in
Room's transaction; they never trigger deletion/reset or silently resend all history.
Only migration code reads old flags. Uncompressed and official databases retain their
normal context behavior. This is an upgrade path, not a downgrade path to 2.5.6.

JVM tests execute the real compatibility migration through sqlite-jdbc against official
and fork 24/25/26 fixtures, checking columns, foreign keys, branches and favorites.
Pure context tests check chunk joining and the actual upstream context selection.
Android device installation/restore remains a separate check.

## Retained features

Image compression is off by default and retains the old DataStore keys and backup
fields. The configured limit is 100–5000 KiB (500 KiB default) for JPEG bytes before
Base64 encoding. GIFs are unchanged. Enabling the option uses 1600px/4MP sampling and
iteratively reduces quality/size; further resizing enforces the limit. The settings
UI uses the new CardGroup design and updates current state through upstream's API.

Markdown export writes on a background dispatcher, supports the reasoning toggle,
propagates cancellation/errors, and replaces message/tool images with placeholders.
It never reads image files or embeds Base64/image URLs. Image export is unchanged.
`{{time}}` remains local time formatted HH:mm.

The Files area has two independent panes; Rootfs retains its upstream browser and
Alpine installation support. Basic/Files switch with bottom buttons; horizontal page
swipes are disabled. The path follows the active pane and uses `/workspace` paths.

Long press provides copy/move/delete/full-name rename/copy path/multi-select, alongside
export/share. Swipe left on two endpoints selects the inclusive range. Both panes
retain their directory, scroll and selection. Names use at most two lines.

Copy/move freezes sources and the opposite pane's target. Existing targets require
replace/skip/rename; directory replacement replaces the whole directory. Transfers
are staged with replacement backups. Root, traversal, ancestor/descendant and escaping
targets are rejected. Recursive deletion does not follow symlinks. Operations do not
run concurrently. Existing workspace regression tests are retained.

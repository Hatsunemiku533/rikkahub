# Patched release builds

Patch base: upstream **2.5.6**, commit `447bb7e89710d31f1204d7a2973baa19fdbd5b28`.
Use `bash scripts/apply-patches.sh <clean-upstream-checkout>` to apply the image
patch, the UX patch, then the workspace-browser patch. Strict application is intentional: do not use fuzzy
repairs, `--reject` or suppressed errors in CI. Future releases can require a rebase.

The fork's application source is not the build input: an upstream release plus
these patches is. Editing only the fork's Kotlin files does not change the APK.
Master patch/CI/script changes trigger the actual build, tests, signing and ntfy.
`verify-build` uses that same pipeline. Manual runs force rebuilding; scheduled
runs compare both the tag and patch/CI fingerprint of the published build.
Compatibility checks run before large cache restores. Cache keys use upstream source.

Patched database schema remains 26 with guarded 24→25 and 25→26 migrations and
unchanged `compressed` / `is_summary` columns. Review future upstream schema changes.

Compression keeps originals and attachments visible, and preserves recent node IDs,
branches and favorites. Recompression uses retained originals, excluding old summaries.
Changed messages during a compression request abort writeback. Unlimited removes
the requested summary-size target; it cannot bypass model context limits or guarantee
lossless summaries. Source messages are no longer silently cut to 2000 characters.

Image compression is optional (off by default), with a 100–5000 KiB JPEG byte limit
(500 KiB default), before Base64 encoding. GIFs remain unchanged. Further resizing
enforces the byte limit after the quality-search budget is exhausted.

Markdown export replaces message and tool-output images with text placeholders,
without reading image files or embedding Base64/URLs. Image export is unchanged.

Tests cover Markdown options/content/image placeholders/streaming/cancellation/errors, preserved recent
branches, stale compression edits/deletions, and generation around archived nodes.

## Workspace file browser

`workspace-browser.patch` adds two independent compact file panes in the Files
area. Rootfs keeps its existing browser. Basic/Files pages switch only with the
bottom navigation buttons; horizontal page swipes are disabled.

The top path follows the last touched pane and uses `/workspace` paths. Tap the
path to view/copy it; refresh and import use that pane. Both panes keep their
own directory, scroll and selection. Long press a file/folder for copy, move,
delete, full-name rename, copy path and multi-select. File export/share reuse
the existing implementation, including batch export and image previews.

Swipe left on the first and last entries to select the inclusive range in
either direction. The second endpoint clears the anchor; subsequent ranges
add to the selection. Tap entries while selecting to toggle them. Back clears
the active selection before navigating up. Names use at most two lines.

Copy/move confirmation freezes the source list and the opposite pane's target
directory. Existing destinations require replace, skip or a different full
filename; folder replacement replaces the whole folder (no implicit merge).
Copies are staged and replacements backed up before commit. Self, descendant,
ancestor, root and escaping targets are rejected. Nested links are copied as
links and cleanup never follows them. A failed restore leaves the backup in
place. File operations do not run concurrently in the browser.

Regression tests cover forward/reverse ranges, panel isolation, stale directory
responses, frozen targets, conflict handling, Unicode/binary transfers, complete
extension changes, overwrite guards, path guards and symlink-safe cleanup.

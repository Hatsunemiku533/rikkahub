# Patched release builds

Patch base: upstream **2.5.6**, commit `447bb7e89710d31f1204d7a2973baa19fdbd5b28`.
Use `bash scripts/apply-patches.sh <clean-upstream-checkout>` to apply the image
patch then the UX patch. Strict application is intentional: do not use fuzzy
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

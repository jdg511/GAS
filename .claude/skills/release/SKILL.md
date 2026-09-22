---
name: release
description: Prepare and publish a verified cross-platform The Great American Spring release.
---

# The Great American Spring Release

When the user enters `/release` (optionally followed by a version), treat it as a request to create a production release.

1. Confirm that the requested version matches `CMakeLists.txt` and that the working tree is clean. Do not use `-AllowDirty` for a real release.
2. Run the local Windows preflight and package step:

   ```powershell
   .\scripts\New-Release.ps1 -Version <version>
   ```

3. Report the local package path and explain that macOS signing/notarization is still required before customer distribution.
4. Ask for explicit approval before the external publishing step. On approval, run:

   ```powershell
   .\scripts\Publish-Release.ps1 -Version <version>
   ```

   This creates and pushes tag `v<version>`. The GitHub Actions release workflow builds Windows, Linux, and universal macOS packages, makes the tracked source-code ZIP, and attaches every package to the matching GitHub Release.

For a safe local rehearsal, use this instead:

```powershell
.\scripts\New-Release.ps1 -Practice
```

Do not claim the GitHub release is complete until the workflow has passed. VST2 and AAX are intentionally excluded because their SDKs are separately licensed and not present in this project.

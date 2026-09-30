# Release output

`New-Release.ps1` writes local rehearsal and preflight packages here. The package folders are intentionally ignored by Git so compiled binaries and generated ZIP files do not bloat the source repository.

For a production release, run the local preflight with `New-Release.ps1` first and then use `Publish-Release.ps1`. The latter pushes the version tag, starting the GitHub Actions workflow, which produces the Windows, Linux, and universal macOS packages and attaches them, along with a tracked source-code ZIP and SHA-256 checksums, to the GitHub Release.

The source-code ZIP is generated with `git archive`, so it contains exactly the committed release revision and excludes the `.git` database and locally generated build output.

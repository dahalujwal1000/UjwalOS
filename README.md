# UjwalOS

A planned Fedora-based x86-64 gaming desktop with KDE Plasma, a familiar
desktop layout, and opt-in Android continuity through KDE Connect.

**Status: Stage 1 implementation in progress.** The description passes KIWI
validation; the isolated build is being tested. See [current evidence](docs/status.md)
for the exact ISO, live boot and installation status.

## Project documents

- [Full product specification and original master prompt](plan.md)
- [Architecture](docs/architecture.md) and [image strategy](docs/decisions/0001-image-strategy.md)
- [Build preparation and test gates](docs/build-and-test.md)
- [Security model](docs/security-model.md)
- [Compatibility and dependency review](docs/compatibility.md)
- [Roadmap](docs/roadmap.md) and [release process](docs/release-process.md)
- [Current status / release notes](docs/status.md)
- [Licensing policy](LICENSES/README.md)

## Safe local checks

From the repository root:

```sh
scripts/build/build-iso.sh --validate
python3 -m unittest discover -s tests/config -v
git diff --check
```

These commands validate the pinned description and repository safeguards without
composing an image. To build and boot-test:

```sh
scripts/build/build-iso.sh
scripts/test/test-iso.sh out/build-XXXXXXXX/result/ACTUAL-NAME.iso
```

Use the actual ISO filename printed by the build. Builds run inside a disposable
QEMU VM; tests use a private virtual disk. Both support software emulation when
KVM is unavailable. See [exact prerequisites and commands](docs/build-and-test.md).

# Security review - 2026-09-30

Remediation update 2026-10-15: source changes now enforce Fedora compose
package signatures, remove builder SSH forwarding and bound Gaming Center
profile reads. Passing regression checks and new-image evidence are tracked in [status](status.md). The
findings below preserve the original review; historical ISO evidence does not
validate these new changes.

Scope: first-party Python, QML, shell build/test/release tooling, RPM specs,
desktop defaults, pinned image definitions, current compose evidence and selected
upstream security documentation. Reviewed worktree based on `78a81bc`; the
untracked owner file `opencode.md` was excluded. This is a source/configuration
review, not a penetration-test certification or a complete distribution CVE scan.
No implementation fixes, host changes, image builds or network probes were made.

## Prioritized findings

### P1 / High: compose does not enforce Fedora RPM signatures

Evidence: `scripts/build/prepare-description.py:25` materializes the upstream
`repositories/core.xml` without adding `package_gpgcheck="true"`. Both active
repository entries in
`out/build-9BaEqZ1c/description/repositories/core.xml:2` and `:7` supply signing
keys but omit signature enforcement. The expanded description also has no
`rpm-check-signatures` setting.

The pinned builder SBOM records `python3-kiwi` 11.0.5-1.4. Its upstream
`kiwi/repository/dnf5.py` writes repository `gpgcheck=0` when the attribute is
absent. Importing a key alone does not turn verification on. The installed host
KIWI implementation has the same behavior.

Impact: an independent package-authenticity check is missing at the point where
RPM content and scriptlets become part of the image/build. An attacker who can
substitute accepted repository metadata/packages could introduce unsigned code.
HTTPS metalinks and metadata/package hashes still provide protection; this is
not evidence that any arbitrary mirror or passive network observer can replace
packages, nor evidence the existing ISO was compromised. This finding concerns
compose configuration, not a claim that installed Fedora DNF disables checking.

Remediation: explicitly require Fedora package signatures for each active
compose repository, validate the effective DNF configuration, and add a negative
test proving unsigned/wrong-key packages are rejected. Keep locally built,
currently unsigned UjwalOS RPM handling separate and explicit. Rebuild and repeat
boot/install gates after fixing. Do not blindly require repository metadata
signatures without checking Fedora's metadata authentication mechanism.

Sources checked 2026-09-30:
- [KIWI repository schema](https://osinside.github.io/kiwi/image_description/elements.html#repository)
- [Exact builder-version DNF backend](https://github.com/OSInside/kiwi/blob/v11.0.5/kiwi/repository/dnf5.py)

### P2 / Medium: unnecessary builder SSH exposed beyond loopback

Evidence: `scripts/build/build-iso.sh:67` uses boxed-plugin defaults with 9p
sharing. `out/build-9BaEqZ1c/build.log:21` records
`hostfwd=tcp::10022-:22`, without a loopback bind address. The installed plugin's
`defaults.py:109` generates this option. The log also records sshd starting in
the builder. The builder can write the exported description and result trees.

Impact: while a compose runs, guest SSH is available through a wildcard-bound
host port, subject to host firewall/network routing. Successful guest compromise
could modify build inputs or outputs. A disposable VM does not protect its
writable shared directories from a compromised guest.

Confirmed: configuration and historical service startup. Not confirmed: LAN
reachability, effective authentication in the pinned guest, or successful login.
Current upstream source contains a fixed root password hash and an unsafe-key
archive, but these alone do not establish remote authentication bypass in the
pinned image. Do not report this as demonstrated remote root access.

Remediation: remove forwarding entirely for the 9p workflow, or restrict it to
loopback with documented authentication when genuinely needed. Test the generated
QEMU arguments and listener binding. Do not depend solely on a host firewall.

Upstream sources checked 2026-09-30 (current main, not proof of pinned contents):
- [Builder definition](https://github.com/OSInside/kiwi/blob/main/boxes/universal/appliance.kiwi)
- [Builder service configuration](https://github.com/OSInside/kiwi/blob/main/boxes/universal/config.sh)

### P3 / Low: profile loading can block the application

Evidence: `apps/gaming-center/profiles.py:37` opens and fully parses the supplied
path without regular-file checks, nonblocking open or a size/profile-count cap.
`apps/gaming-center/main.py:27` calls it synchronously during startup.

A temporary named-pipe fixture reproduced a load that did not return; the test
terminated and reaped its subprocess after one second. No personal profile was
modified. Large files also have no explicit resource bound, although an
out-of-memory test was deliberately not run. A separate deeply nested JSON test
was rejected as an unsupported document; no recursion-crash finding is claimed.

Impact requires write access to the user's profile location or introduction of
such a file through restore/sync. It is a local availability issue, not remote
code execution or privilege escalation. The private profile directory reduces
cross-user exposure.

Remediation: use a bounded, nonblocking regular-file reader, define a symlink
policy, limit bytes and profile count, and add malformed/special-file tests.

## Release security gaps, not demonstrated exploits

1. **High priority before distribution: artifact authentication.**
   `scripts/release/artifacts.py:94` verifies hashes against a colocated unsigned
   manifest. Replacing both passes the integrity check by design. Establish
   signed manifests and an independently trusted verification key before public
   use. The tool already accurately labels its output unsigned engineering data.
2. **High priority before supporting installed machines: custom-package updates.**
   `scripts/build/prepare-description.py:58` installs three local UjwalOS RPMs;
   this repository does not provision a signed UjwalOS update repository.
   Fedora updates do not distribute fixes to these custom packages. Establish
   an authenticated update path and test delivery of a versioned security fix.
3. **Unfinished distribution/runtime assessment.** No complete Fedora advisory
   correlation was performed for every package in the ISO. Secure Boot,
   installed-system firewall/listeners, SELinux enforcement, disk encryption,
   live-account cleanup, multi-user boundaries and triple-boot safety need
   separate runtime verification. Missing evidence is not a confirmed exploit.

## Dependency advisory check

The latest ISO manifest lists KDE Connect 26.08.1-1.fc44. KDE's
[CVE-2025-66270 advisory](https://mail.kde.org/pipermail/kde-announce/2025-November/000476.html)
affects desktop versions >=25.04 and <25.12, so this recorded desktop version is
outside that range. Android versions >=1.33.0 and <1.34.4 are affected; the owner's
phone version is unknown and must be checked. This single check does not certify
all dependencies or all KDE Connect functionality as vulnerability-free.

No Bandit, ShellCheck, Trivy or Grype executable was available. Nothing was
installed on the host. A limited tracked-text secret-pattern search found no
matching private-key headers, GitHub-token patterns or AWS access-key IDs; this
is not an exhaustive secret/history scan.

## Verification

- `python3 -m unittest discover -s tests/config -v`: 35 passed.
- `QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software out/stage4-venv/bin/python -m unittest discover -s tests/ui -v`: 13 passed.
- `dbus-run-session -- out/stage4-venv/bin/python tests/integration/test_phone_transport.py -v`: 2 passed with an isolated synthetic bus. Initial sandbox attempt could not bind a socket; permitted rerun passed.
- Temporary FIFO profile-load reproducer: blocking confirmed; subprocess killed
  and reaped, temporary fixture removed.
- Targeted source and historical compose-log inspection; exact KIWI 11.0.5 DNF
  backend and selected public upstream documentation checked read-only.

Existing tests passing does not invalidate these findings. Add security-specific
regression tests alongside fixes. No fixes are represented by this report, and
the existing ISO has not been rebuilt or newly certified.

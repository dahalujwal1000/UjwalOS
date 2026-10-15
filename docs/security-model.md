# Initial security model

This is a planning threat model, not a completed security audit.

A bounded [source/configuration security review](security-review-2026-09-30.md)
was completed on 2026-09-30. Source fixes and regression checks passed on
2026-10-15 for P1 compose RPM signature enforcement, P2 builder SSH exposure and
P3 profile-file blocking. The corrected ISO passed compose and media checks;
live boot, installation and installed runtime validation remain pending. See
[status](status.md). Required controls below must not be read as already
verified. Signed artifacts, an authenticated custom-package update channel,
complete dependency review and installed runtime security tests remain
outstanding. The 63 automated test passes are not security certification (48 configuration, 13 UI
and 2 isolated D-Bus tests passed on 2026-10-15).

| Asset / boundary | Threat | Required control and validation |
| --- | --- | --- |
| Host versus builder | Compose damages host or disks | Disposable builder, no physical disk passthrough, inspect privileged build scripts |
| Boot chain and update sources | Tampered kernel, RPM, or image | Fedora trust chain, signed RPM verification, authenticated sources, verifiable release artifacts |
| User UI versus privileged service | Arbitrary root command execution | Narrow typed D-Bus methods, PolicyKit, caller validation, no shell passthrough |
| Performance state | Settings persist after a crash | Durable prior-state record, bounded changes, restoration tests including reboot |
| PC versus Android device | Unauthorized pairing or access | Explicit pairing, encrypted transport, protected keys, per-feature consent, revoke/unpair |
| Phone content and diagnostics | Private data leaks | Local processing by default, no cloud uploads, opt-in redacted diagnostics |
| Optional external software | Untrusted installation or unclear rights | User initiation, verified origin, separate licensing and removal review |

Never disable thermal controls, SELinux, update services, or essential security
controls for benchmarks. Secure Boot signing and NVIDIA module enrollment need
separate documented testing; Fedora's signed kernel does not certify a remix ISO.
Do not collect pairing keys, phone content, usernames, serial numbers, MAC
addresses, or network identifiers in default diagnostic reports.

For future phone features, document permission changes, lost/stolen paired-device
revocation, reconnection, and multiple-user isolation. For each privileged method,
specify authorization, inputs, failure messages, state ownership, and recovery.

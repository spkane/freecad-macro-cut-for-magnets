# Cut Object for Magnets Release Plan

**Assessment date:** 2026-09-04  
**Current source version:** 0.6.2  
**Recommended next release:** 0.7.0 after a release candidate and manual UAT  
**Current recommendation:** Do not submit to the official FreeCAD Addon Index yet.

## Executive Summary

This is already a substantial FreeCAD tool, not a small throwaway macro. The
repository includes a manifest, user documentation, unit and FreeCAD tests, security
checks, CI, install helpers, and an automated release process. A GitHub release tagged
`macro-cut-object-for-magnets-v0.6.2` exists. The repository is not yet present in the
official FreeCAD Addon Index, and the current gaps should be closed before submitting
it.

The biggest risk is that tests do not exercise the implementation users run.
`CutObjectForMagnets.FCMacro` contains the 1,300-line `SmartCutter` and almost all
geometry/document behavior. It imports only `HolePlacementError` from the modular
code. The FreeCAD integration suite instead tests helper functions in
`cut_magnets_fc.py`; it never executes `SmartCutter.execute()`. Passing tests therefore
do not currently prove that the actual macro can safely complete, recover, or produce
valid aligned holes.

The core algorithm also has several release-significant edge cases: the cutting
half-space is centered around the global origin rather than the object's bounds;
parameter validation exists in a module the macro does not call; a permissive cylinder
heuristic can mistake ordinary cylindrical surfaces for existing holes; fallback face
selection knowingly permits the wrong face; and eight separately committed FreeCAD
transactions can leave a partially modified document after a later failure.

The recommended path is a focused 0.7 release: make one canonical engine, test the
real operation end to end, harden the geometry and rollback behavior, validate current
FreeCAD packaging, and then submit that stable release to `FreeCAD/Addons`.

## Codebase Map

| Area | Purpose | Release relevance |
| --- | --- | --- |
| `macro/Cut_Object_for_Magnets/CutObjectForMagnets.FCMacro` | GUI, entry point, `SmartCutter`, geometry, PartDesign feature creation, and document transactions | Actual production implementation; 1,928 lines and only lightly connected to tested modules |
| `macro/Cut_Object_for_Magnets/cut_magnets_core.py` | Dataclasses, validation, vector-free calculations, summaries | 98% covered, but much of it is not called by the macro |
| `macro/Cut_Object_for_Magnets/cut_magnets_fc.py` | FreeCAD helper functions for cuts, faces, safety, and existing holes | Integration-tested duplicate of some macro logic, not the production engine |
| `macro/Cut_Object_for_Magnets/__init__.py` | Version/package metadata | Starting point for a canonical namespaced package |
| `tests/unit/test_core.py` | Pure-Python parameter/math tests | 60 tests passed, but production wiring is missing |
| `tests/freecad/test_cut_magnets.py` | FreeCAD tests for helper functions | Does not load the macro, instantiate `SmartCutter`, or validate final paired bodies |
| `tests/just_commands/` | Syntax/runtime tests for task recipes | 63 tests passed in this audit |
| `package.xml` | Addon Manager metadata and macro declaration | Must validate against the current manifest schema and actual package layout |
| `docs/`, `README.md`, macro README/wiki source | User and release documentation | Generally extensive; some links, versions, and algorithm claims are stale |
| `just/`, `scripts/release-helpers.sh` | Local setup, checks, install, and release helpers | Good foundation, but the release gate omits the real FreeCAD operation |
| `.github/workflows/` and `.github/actions/` | CI, docs, CodeQL, FreeCAD setup, and releases | Good breadth; currently stale version matrix and disabled scheduled CodeQL |

### Runtime flow today

1. FreeCAD executes `CutObjectForMagnets.FCMacro`.
2. The macro prepends its directory to `sys.path` and imports only
   `HolePlacementError` (`CutObjectForMagnets.FCMacro:44-63`).
3. Dialog values are returned as a dictionary. The reusable `HoleParameters` and
   `validate_cut_parameters()` logic are not invoked.
4. The macro-local `SmartCutter` cuts geometry, chooses faces, validates/repositions
   holes, creates two bodies and their features, separates one body by 100 mm, and
   hides inputs.
5. The operation commits eight transactions independently
   (`CutObjectForMagnets.FCMacro:1303-1434`). A failure after an early commit leaves
   earlier output in the document.

The target flow should use a canonical package engine called by a thin macro command,
validate before mutation, compute all geometry before mutation where possible, and
commit the user-visible operation atomically.

## Verified Baseline

The following checks were run against the working tree during this assessment:

| Check | Result |
| --- | --- |
| Pure-Python test runtime | CPython 3.11 |
| FreeCAD integration runtime | Not run locally; CI currently pins FreeCAD 1.0.0, while FreeCAD 1.1.3 is the current stable target to certify |
| Unit tests | 60 passed |
| Unit-test coverage | 41% package total; `cut_magnets_core.py` 98%; FreeCAD module 0% under normal pytest |
| Just command tests | 63 passed |
| MkDocs strict build | Passed |
| Ruff, Ruff format, Bandit, gitleaks, detect-secrets, codespell, Markdown/YAML/action checks | Passed |
| Full `just all` | All substantive hooks passed; command failed only because `no-commit-to-branch` rejects `main` |
| `uv.lock` resolution | Resolved successfully |
| Local FreeCAD integration suite | Not runnable: the installed weekly macOS build aborts in this execution environment with a Qt `neon` processor-feature error |
| Official Addon Index | Repository URL not present in `FreeCAD/Addons` `Data/Index.json` on 2026-09-04 |
| Scheduled CodeQL | Workflow state is `disabled_inactivity`; the last scheduled success was 2026-03-22 |
| Dependency backlog | 17 open Dependabot pull requests, all development/docs/Actions dependencies |

The local integration limitation must not be treated as a pass. Fresh FreeCAD CI and
manual GUI UAT are required before release.

## Release Blockers

### P0. Make the production engine canonical and test it directly

**Evidence:** The `.FCMacro` imports only `HolePlacementError`
(`CutObjectForMagnets.FCMacro:44-63`) and defines `SmartCutter` at line 427. The
FreeCAD suite imports `cut_magnets_fc` helpers (`tests/freecad/test_cut_magnets.py:17-36`)
and its explicit suite contains no `SmartCutter` test
(`tests/freecad/test_cut_magnets.py:417-448`). Similar algorithms already differ or
are duplicated across the two files.

**Work:**

- Move `SmartCutter` and its geometry/document collaborators into a canonical
  FreeCAD package using the modern `freecad/<AddonName>/` namespace.
- Make the `.FCMacro` file a thin entry point that imports and invokes the package.
- Remove duplicate helper implementations after tests target the canonical code.
- If single-file installation remains supported, generate that artifact from the
  canonical modules and test it; do not maintain a second handwritten engine.
- Remove `sys.path` mutation and assert the loaded module's origin in smoke tests.
- Add integration tests that instantiate the real cutter, execute the full operation,
  inspect both final bodies and holes, and verify failure cleanup.

**Acceptance criteria:** The same `SmartCutter` code is used by Addon Manager,
standalone artifact, integration tests, and GUI invocation; CI fails on any fallback or
duplicate implementation drift.

### P0. Replace the origin-centered cutting half-space

**Evidence:** `cut_object()` takes the largest bounding-box dimension, makes a cube
centered around global XY origin, rotates it, and translates it only by the plane
point (`CutObjectForMagnets.FCMacro:605-646`). The tested duplicate does the same
(`cut_magnets_fc.py:89-116`). A translated object, long/thin object, or oblique plane
can extend outside this cube, yielding incomplete or empty cuts.

**Work:** Build a bounded half-space from all object bounding-box corners expressed in
the cut plane's local coordinate frame, with a tolerance margin in both tangent axes
and sufficient normal depth. Alternatively use a robust OpenCASCADE half-space API if
it is stable across the supported FreeCAD range. Validate that both results are
non-null, valid solids with meaningful positive volume before creating document
objects.

**Acceptance criteria:** Tests pass for objects translated far from origin, extreme
aspect ratios, all preset axes, oblique datum planes, planes near a boundary, and
planes outside the object. Outside/tangent cuts fail before document mutation with an
actionable message.

### P0. Wire parameter and object validation into execution

**Evidence:** The UI independently permits preferred and minimum clearances between
0.1 and 20 mm (`CutObjectForMagnets.FCMacro:156-174`). `HoleParameters.validate()`
correctly rejects preferred clearance below minimum
(`cut_magnets_core.py:66-103`), but the macro never constructs it or calls
`validate_cut_parameters()`; `main()` validates only model-plane selection before
creating the cutter (`CutObjectForMagnets.FCMacro:1869-1899`).

**Work:**

- Use the core dataclasses as the typed boundary between dialog and engine.
- Validate clearance ordering, diameter, depth, hole count, plane normal, selected
  object's validity/solidity, active document ownership, and the model-face reference.
- Link spinbox constraints so invalid combinations are hard to enter, while retaining
  engine validation for scripts and restored preferences.
- Reject a depth that cannot preserve material in both halves instead of relying only
  on later boolean-volume tolerance.

**Acceptance criteria:** Invalid input cannot mutate the document; every validation
rule has both unit and GUI/engine-boundary coverage.

### P0. Make the operation atomic and validate final geometry

**Evidence:** Eight transactions commit independently
(`CutObjectForMagnets.FCMacro:1303-1434`). If top-body or hole creation fails, earlier
bodies/sketches remain. `_create_hole_feature()` computes `is_valid` but only logs it
and returns the feature (`CutObjectForMagnets.FCMacro:1694-1739`). The original is
hidden only near the end, so failure states vary with the failing step.

**Work:**

- Compute and validate both cut shapes and all positions before creating document
  objects.
- Wrap the complete user operation in one transaction when FreeCAD semantics allow
  it. Otherwise track every created object and prior visibility/placement value and
  restore/remove them on failure.
- After recompute, require both bodies and both hole features to be valid, have
  positive volume, contain the requested number of holes, and remain aligned.
- Treat failed separation as a surfaced warning in the final result, and make
  separation optional/configurable rather than a fixed 100 mm
  (`CutObjectForMagnets.FCMacro:1389-1410`).
- Add an idempotent recovery test that injects failure at each mutation stage.

**Acceptance criteria:** A failed command leaves no new objects or changed visibility
and placement. A reported success guarantees validated bodies and hole features.

### P0. Tighten hole recognition, placement, and face attachment

**Evidence:** Any cylindrical face with radius <=10 mm passes the existing-hole filter,
regardless of target radius (`CutObjectForMagnets.FCMacro:443-485`). This can classify
an outside cylinder or unrelated fillet/feature as a magnet hole. Existing positions
are exempted from overlap rejection (`CutObjectForMagnets.FCMacro:1274-1284`). If no
face is close to the current plane, `_find_cut_face_name()` knowingly uses the best
normal match even if it belongs to a prior cut
(`CutObjectForMagnets.FCMacro:1619-1627`).

**Work:**

- Recognize holes using target-radius tolerance, concavity/internal orientation,
  axis/plane relationship, circular edge closure, and depth along the cylinder axis.
- Deduplicate projected positions and apply overlap rules to existing and new holes.
- Attach sketches only to a face positively identified as the new cut face using
  plane distance, orientation, and geometric identity. Fail if confidence is
  insufficient; do not choose a potentially wrong face for convenience.
- Replace the bounding-box maximum used as cylinder depth with projection along the
  detected cylinder axis.
- Make containment tolerance explicit and evidence-based. Code accepts 95% and tests
  only `depth - 0.5`, while documentation describes a cylinder extended by depth plus
  clearance (`CutObjectForMagnets.FCMacro:711-745`,
  `docs/parameters.md:106-107`). For depths <=0.5 mm the current function simply
  returns safe.

**Acceptance criteria:** Tests distinguish interior holes from exterior cylinders,
fillets, bosses, and unrelated bores; shallow and edge cases fail conservatively;
re-cut holes stay aligned without duplicates; face ambiguity stops safely.

### P0. Establish a current FreeCAD compatibility gate

**Evidence:** CI pins FreeCAD 1.0.0 (`.github/workflows/tests.yaml:71-87`) while the
latest stable release is 1.1.3. The manifest claims 0.21+ (`package.xml:16`) without a
tested version matrix. FreeCAD 1.1.3 contains security fixes and ships Python 3.11,
while `pyproject.toml:7` permits any Python >=3.11; during this audit an unqualified
`uv run` selected Python 3.13 in the sibling macro repository using the same setup.

**Work:**

- Test current stable FreeCAD 1.1.3 and the actual full `SmartCutter` flow in CI.
- Test the oldest release that remains in `<freecadmin>`, or raise the minimum to the
  oldest version that receives automated and manual coverage.
- Constrain pure-Python development to `>=3.11,<3.12` (or equivalent) while stable FreeCAD
  embeds 3.11, add `.python-version`, and use `uv run --python 3.11` only for pure-Python recipes.
- Keep FreeCAD integration recipes and CI on `freecadcmd`; fail CI if FreeCAD's bundled Python minor version differs from the expected version.
- Perform manual GUI tests on macOS arm64, Windows x64, and Linux x64.

**Acceptance criteria:** Manifest compatibility claims match green CI/manual evidence,
and no supported workflow accidentally runs against Python 3.12+.

## Priority Improvements

### P1. Make release automation a real gate

- Change bare `pytest` calls to pinned `uv run` commands
  (`just/testing.just:14-24,74-84`). Current recipes depend on a separately activated
  environment.
- Add real `SmartCutter` integration, strict docs, manifest validation,
  installed-layout smoke, generated standalone smoke, and archive-content validation
  to `release-test`. Its current three steps cover unit tests, just tests, and
  pre-commit only (`just/testing.just:113-164`).
- Reconcile `no-commit-to-branch` with release checks: the hook rejects `main`, while
  `scripts/release-helpers.sh:17-29` requires tagging from `main`.
- Add `uv.lock`, `.mise.toml`, `just/**`, `package.xml`, and the local FreeCAD setup
  action to the Tests workflow path filters.
- Add job timeouts and explicit exit propagation for the FreeCAD command wrapper.
- Fix release-note generation. The step says “Extract release notes” but constructs a
  generic body and never reads `RELEASE_NOTES.md`
  (`macro-release-reusable.yaml:207-259`).

### P1. Choose and validate the distribution contract

The recommended contract is an indexed standalone addon repository using the modern
namespace layout, plus a generated `.FCMacro` for manual users.

- Validate `package.xml` with the current Stable Addon Manifest Schema. Its namespace
  points at the older wiki metadata URL (`package.xml:2`); migrate according to current
  validator output.
- Confirm the `<macro>` content, subdirectory, and icon are interpreted correctly by
  the current Addon Manager.
- Current custom GitHub archives copy only the `.FCMacro`, icon, README, and LICENSE
  (`macro-release-reusable.yaml:163-202`). They omit the tested modules and
  `package.xml`. Give addon-source and standalone artifacts distinct names and smoke
  test both contracts.
- Add checksums and, if practical, GitHub artifact attestations.
- Consider the Addon Academy's recommended stable release branch once packaging is
  settled, and keep the manifest branch attribute synchronized.

### P1. Synchronize documentation and actual behavior

- Change Addon Manager instructions to “not yet indexed” until acceptance.
- Fix the unrelated documentation URL in
  `macro/Cut_Object_for_Magnets/README-CutObjectForMagnets.md:9`.
- Add 0.6.2 to `docs/changelog.md`; it currently stops at 0.6.1.
- Remove the obsolete claim that the release is being added to the maintainer's
  `FreeCAD-addons` fork (`macro/Cut_Object_for_Magnets/RELEASE_NOTES.md:17`). The
  modern official index is `FreeCAD/Addons`.
- Reconcile the safety algorithm docs with actual, tested containment semantics. Do
  not claim “depth + clearance” while code evaluates a shorter cylinder at a 95%
  volume threshold.
- Document supported solids, behavior for existing holes, multi-solid results, model
  plane lifetime, partial-failure recovery, output-body placement, and the fact that
  runtime code performs no network activity.
- Make one version/date source update the project, both manifest entries, package,
  macro metadata, README/docs, wiki source, release notes, and lockfile; fail CI on
  disagreement.

### P1. Refresh dependencies and CI supply-chain controls

- Review the 17 open Dependabot PRs in batches: security/transitive packages,
  test/lint tools, docs tools, and then Actions. Run the complete release gate after
  each batch and close superseded PRs.
- Remove the unused Docker Dependabot ecosystem; no Dockerfile exists
  (`.github/dependabot.yaml:41-60`).
- Pin third-party GitHub Actions to full commit SHAs with version comments and retain
  Dependabot for updates.
- Re-enable CodeQL, run it on the release candidate, and confirm GitHub private
  vulnerability reporting is enabled.
- Add `SECURITY.md` with supported versions, a private reporting route, and response
  expectations. Add `CODEOWNERS` if branch protection will require review.

### P2. Maintainability and UX

- Split the engine into narrow collaborators: cut-plane geometry, cut validation,
  hole detection, placement, PartDesign construction, and transaction/recovery.
- Replace untyped parameter dictionaries with dataclasses through the full call chain.
- Store exact FreeCAD object identity in combo-box item data instead of substring
  matching labels (`CutObjectForMagnets.FCMacro:255-283`). Duplicate labels are legal.
- Add a non-mutating preview showing the cut plane, candidate hole centers, skipped or
  repositioned holes, and clearance failures before the user commits.
- Let the user choose no separation, automatic bounding-box-based separation, or a
  custom distance rather than always moving the top body 100 mm.
- Provide a single Undo result and a concise structured completion report containing
  holes requested, retained, repositioned, skipped, and created.
- Add translations only after UI terminology and parameters stabilize.
- Add the GitHub repository topics `freecad` and singular `addon`.

## Security Assessment

The macro has no runtime network connections, subprocess execution, credentials,
dynamic package installation, or third-party runtime Python dependencies. Static
Bandit, secret scanners, and the last active CodeQL runs found no critical remote
code-execution issue in this repository.

The dominant risks are local document integrity and build/release supply chain rather
than confidentiality:

| Boundary | Main risk | Planned control |
| --- | --- | --- |
| Selected FreeCAD document | Malformed/unexpected geometry or a vulnerable old FreeCAD build | Require current stable FreeCAD, validate object/shape, robust boolean tests |
| Existing document state | Partial bodies/features or hidden/moved inputs after failure | Atomic transaction or explicit rollback, injected-failure tests |
| Geometry heuristics | Wrong cylinder or face selected, producing incorrect/unsafe print geometry | Conservative recognition, no guessed face fallback, final validity/alignment checks |
| Addon import namespace | Top-level module collision after `sys.path` manipulation | Namespaced package, no path mutation, asserted import origin |
| CI/release dependencies | Compromised mutable action tag or stale dependency | SHA pinning, Dependabot batches, CodeQL re-enable, least privilege |
| Release artifacts | Installed content differs from tested source | Deterministic generation, content smoke tests, checksums/attestation |

FreeCAD 1.1.3 specifically includes fixes for code-execution and file-handling
vulnerabilities triggered by malicious FCStd files. Release documentation and CI/UAT
should use 1.1.3 or newer stable maintenance releases rather than encouraging testing
on older 1.1 builds.

Keep workflow permissions job-scoped. The release job's `contents: write` permission
is appropriate for creating releases; other jobs should remain read-only except for
the narrow Pages and security-event permissions they require.

## Required Test and UAT Matrix

### Automated FreeCAD tests

- Execute the canonical `SmartCutter` on FreeCAD 1.1.3 and the declared minimum.
- Preset XY/XZ/YZ planes, datum planes, selected planar faces, oblique planes, and
  reversed normals.
- Box, cylinder, ring/hollow solid, thin wall, curved shell converted to a solid,
  extreme aspect ratio, object translated far from origin, previously cut body, and
  a body with unrelated cylindrical faces.
- Plane through center, near boundary, tangent, and completely outside the shape.
- Preferred clearance below minimum, very shallow depth, depth exceeding one half,
  excessive diameter/count, duplicate labels, stale model-face reference, and invalid
  or multi-solid source.
- Existing true magnet holes, external cylinders/bosses, fillets, unrelated bores,
  duplicate projections, and overlapping old/new holes.
- Assert valid positive-volume bodies; exact requested/accepted hole counts; paired
  center alignment; expected hole direction/depth/diameter; preserved source geometry;
  and no unexpected objects.
- Inject failures after each document mutation and assert full rollback.
- Load through both installed package and generated standalone artifact and assert the
  same implementation origin and results.

### Manual GUI UAT

Run the release candidate on macOS arm64, Windows x64, and Linux x64 with current
stable FreeCAD. Verify selection defaults and duplicate labels, parameter validation,
saved preferences, every plane type, preview if added, progress, cancellation/error
recovery, one-step Undo, repeated cuts, editable PartDesign holes, installation,
uninstall/reinstall, and standalone use. Print or slice representative outputs where
practical; geometric validity alone does not prove magnet fit or wall durability.

Record the FreeCAD build, OS, model, parameter set, expected result, actual result,
and resulting FCStd file in the release issue.

## Ordered Release Sequence

1. **Distribution decision:** Adopt namespaced addon source plus a generated
   standalone macro and choose the branch the official index will track.
2. **0.7 architecture change:** Move `SmartCutter` to the canonical package, remove
   duplicates and `sys.path` mutation, and make tests execute the real engine.
3. **Geometry correctness change:** Replace the cutting half-space, validate both
   halves, tighten existing-hole detection, remove guessed face attachment, and align
   containment behavior with documented guarantees.
4. **Document-integrity change:** Wire typed validation, implement atomic rollback,
   validate final PartDesign features, and make body separation configurable.
5. **Compatibility change:** Pin Python 3.11, test FreeCAD 1.1.3 and the supported
   minimum, and repair local/CI release gates.
6. **Packaging and metadata change:** Validate the manifest, define artifact contents,
   synchronize docs/versions, add security policy, and refresh dependencies/actions.
7. **Release candidate:** Publish `0.7.0-rc.1`, perform cross-platform GUI and print-fit
   UAT, resolve release blockers, and rerun every gate from a clean checkout.
8. **Stable release:** Publish 0.7.0 with real release notes, checksums, and verified
   install/uninstall. Delay 1.0 until indexed-user feedback and at least one maintenance
   release demonstrate stability.
9. **Official submission:** Open an “Addon - Addition” request in `FreeCAD/Addons`
   with the manifest, security policy, compatibility matrix, latest release,
   documentation, and UAT evidence; respond to reviewer feedback.
10. **Post-release:** Verify indexed installation after refresh, monitor issues and
    security reports, and schedule a 0.7.1 maintenance window.

## Release Go/No-Go Checklist

- [ ] GUI, installed addon, tests, and standalone artifact use one canonical engine.
- [ ] No runtime `sys.path` mutation or ambiguous top-level addon imports remain.
- [ ] Full `SmartCutter.execute()` integration tests validate both final bodies.
- [ ] Translated, oblique, edge, tangent, and outside-plane cuts behave safely.
- [ ] Invalid input is rejected before document mutation.
- [ ] Failures at every stage restore document objects, visibility, and placement.
- [ ] Existing-hole detection rejects unrelated exterior/cylindrical geometry.
- [ ] Face attachment never falls back to a knowingly ambiguous face.
- [ ] Final holes are valid, aligned, non-overlapping, and match requested dimensions.
- [ ] Documentation and code use the same tested clearance/containment definition.
- [ ] FreeCAD 1.1.3 and the declared minimum pass CI/manual tests.
- [ ] Every dev/test command is constrained to the FreeCAD Python 3.11 ABI.
- [ ] Current manifest validation passes with accurate content and branch data.
- [ ] Strict docs, real FreeCAD integration, package/archive smoke tests, static checks,
      secrets scans, and CodeQL all pass from a clean checkout.
- [ ] Version/date values and `uv.lock` agree everywhere.
- [ ] Addon Manager is not advertised as available until the listing is live.
- [ ] `SECURITY.md`, supported versions, and a private reporting route are published.
- [ ] Dependency updates are triaged and release Actions are SHA-pinned.
- [ ] 0.7.0 assets, notes, checksums, install, uninstall, and one-step Undo are verified.
- [ ] Official Addon Index review is complete and installation from the index works.

## Authoritative References

- [FreeCAD Addon Index](https://github.com/FreeCAD/Addons)
- [FreeCAD Addon Index quality requirements](https://freecad.github.io/Addon-Academy/Topics/Addon-Index/Index/Qualities)
- [FreeCAD addon types](https://freecad.github.io/Addon-Academy/Topics/Types/)
- [FreeCAD compatibility guidance](https://freecad.github.io/Addon-Academy/Guides/Maintaining/Compatibility/)
- [FreeCAD metadata and discoverability guidance](https://freecad.github.io/Addon-Academy/Guides/Polish/Metadata/)
- [FreeCAD Addon Manifest Schema](https://github.com/FreeCAD/Addon-Manifest-Schema/tree/Stable)
- [FreeCAD releases](https://github.com/FreeCAD/FreeCAD/releases)

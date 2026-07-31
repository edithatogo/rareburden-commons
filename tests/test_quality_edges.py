from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path

import pytest

import rareburden.release as release_module
from rareburden.burden import (
    BurdenInputError,
    IntervalEstimate,
    _quantile,
    expected_affected_population,
    rare_aetiology_cases,
    simulate_fraction_product,
)
from rareburden.provenance import (
    ArtifactRecord,
    ProvenanceError,
    atomic_write_bytes,
    build_manifest,
    content_id,
    git_commit,
    register_local_artifact,
    sha256_file,
    stable_identifier,
)
from rareburden.release import ReleaseManifestError, build_release_manifest, verify_release_manifest


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ((-1, None, None, "people", "observed"), "estimate"),
        ((math.inf, None, None, "people", "observed"), "estimate"),
        ((1, None, None, " ", "observed"), "unit"),
        ((1, None, 2, "people", "observed"), "supplied together"),
        ((1, 0, None, "people", "observed"), "supplied together"),
        ((1, -1, 2, "people", "observed"), "finite and non-negative"),
        ((1, 2, 3, "people", "observed"), "contain the estimate"),
    ],
)
def test_interval_estimate_rejects_invalid_contracts(
    arguments: tuple[object, ...], message: str
) -> None:
    with pytest.raises(BurdenInputError, match=message):
        IntervalEstimate(*arguments)  # type: ignore[arg-type]


def test_burden_functions_reject_incompatible_units_and_bounds() -> None:
    people = IntervalEstimate(100, None, None, "people", "observed")
    proportion = IntervalEstimate(0.1, None, None, "proportion", "modelled")
    with pytest.raises(BurdenInputError, match="population must"):
        expected_affected_population(
            IntervalEstimate(100, None, None, "persons", "observed"), proportion
        )
    with pytest.raises(BurdenInputError, match="prevalence must"):
        expected_affected_population(people, IntervalEstimate(1, None, None, "people", "observed"))
    with pytest.raises(BurdenInputError, match="case envelope"):
        rare_aetiology_cases(IntervalEstimate(100, None, None, "cases", "observed"), proportion)
    with pytest.raises(BurdenInputError, match="aetiology fraction"):
        rare_aetiology_cases(people, IntervalEstimate(1, None, None, "people", "observed"))
    with pytest.raises(BurdenInputError, match="between 0 and 1"):
        rare_aetiology_cases(people, IntervalEstimate(0.5, 0.1, 1.1, "proportion", "modelled"))

    result = expected_affected_population(people, proportion)
    assert result.lower is None
    assert result.upper is None


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"envelope": -1}, "envelope"),
        ({"fraction_mean": 0}, "fraction_mean"),
        ({"fraction_mean": 1}, "fraction_mean"),
        ({"fraction_effective_sample_size": 2}, "effective_sample_size"),
        ({"fraction_effective_sample_size": math.inf}, "effective_sample_size"),
        ({"draws": 99}, "draws"),
        ({"draws": 10_000_001}, "draws"),
        ({"unit": " "}, "unit"),
    ],
)
def test_fraction_simulation_rejects_invalid_inputs(
    kwargs: dict[str, object], message: str
) -> None:
    arguments: dict[str, object] = {
        "envelope": 1000,
        "fraction_mean": 0.1,
        "fraction_effective_sample_size": 100,
        "draws": 100,
        "unit": "people",
    }
    arguments.update(kwargs)
    with pytest.raises(BurdenInputError, match=message):
        simulate_fraction_product(**arguments)  # type: ignore[arg-type]


def test_quantile_validates_domain_and_exact_endpoints() -> None:
    with pytest.raises(BurdenInputError, match="no values"):
        _quantile([], 0.5)
    with pytest.raises(BurdenInputError, match="between 0 and 1"):
        _quantile([1.0], -0.1)
    assert _quantile([1.0, 2.0, 3.0], 0) == 1.0
    assert _quantile([1.0, 2.0, 3.0], 1) == 3.0


@pytest.mark.parametrize(
    ("prefix", "length"),
    [("Bad", 24), ("bad_prefix", 24), ("ok", 7), ("ok", 65)],
)
def test_content_id_rejects_invalid_prefix_or_length(prefix: str, length: int) -> None:
    with pytest.raises(ProvenanceError):
        content_id(prefix, {"value": 1}, length=length)


def test_stable_identifier_prefix_and_distinct_inputs() -> None:
    with pytest.raises(ProvenanceError, match="prefix"):
        stable_identifier("value", prefix="***")
    first = stable_identifier("A B", prefix="source")
    second = stable_identifier("A-B", prefix="source")
    assert first != second
    assert first.startswith("source-a-b-")


def test_provenance_hash_write_and_registration_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(ProvenanceError, match="Unable to hash"):
        sha256_file(tmp_path / "missing.bin")
    with pytest.raises(ProvenanceError, match="regular file"):
        register_local_artifact(
            source_id="source",
            release_id="release",
            source_url="https://example.org/data",
            artifact_path=tmp_path / "missing.bin",
            expected_sha256=None,
        )

    target = tmp_path / "target.txt"
    target.write_text("trusted", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)
    with pytest.raises(ProvenanceError, match="symlink"):
        atomic_write_bytes(link, b"replacement")
    assert target.read_text(encoding="utf-8") == "trusted"

    artifact = tmp_path / "fixture.unknownext"
    artifact.write_bytes(b"data")
    manifest = register_local_artifact(
        source_id="source",
        release_id="release",
        source_url="https://example.org/data",
        artifact_path=artifact,
        expected_sha256=None,
        retrieved_at="2026-07-19T00:00:00Z",
    )
    assert manifest["pinning"]["status"] == "candidate_unpinned"
    assert manifest["artifact"]["media_type"] == "application/octet-stream"


def test_build_manifest_rejects_digest_mismatch() -> None:
    artifact = ArtifactRecord("data.bin", "1" * 64, 1, "application/octet-stream")
    with pytest.raises(ProvenanceError, match="Checksum mismatch"):
        build_manifest(
            source_id="source",
            release_id="release",
            method="direct_download",
            requested_url="https://example.org/data",
            resolved_url="https://example.org/data",
            artifact=artifact,
            expected_sha256="0" * 64,
            etag=None,
            last_modified=None,
        )


def test_git_commit_returns_none_without_repository(tmp_path: Path) -> None:
    assert git_commit(None) is None
    assert git_commit(tmp_path) is None


def _release_fixture(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    artifact = tmp_path / "result.txt"
    artifact.write_text("trusted\n", encoding="utf-8")
    manifest = build_release_manifest(
        root=tmp_path,
        artefact_paths=[artifact],
        release_id="fixture-release",
        software_version="0.3.0rc1",
        created_at="2026-07-19T00:00:00Z",
        git_commit="1" * 40,
    )
    return artifact, manifest


def test_release_builder_rejects_invalid_root_empty_and_duplicates(tmp_path: Path) -> None:
    with pytest.raises(ReleaseManifestError, match="not a directory"):
        build_release_manifest(
            root=tmp_path / "missing",
            artefact_paths=[tmp_path / "missing.txt"],
            release_id="release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )
    with pytest.raises(ReleaseManifestError, match="At least one"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[],
            release_id="release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )

    artifact = tmp_path / "artifact.txt"
    artifact.write_text("data", encoding="utf-8")
    with pytest.raises(ReleaseManifestError, match="Duplicate release artefact"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[artifact, artifact],
            release_id="release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )
    with pytest.raises(ReleaseManifestError, match="Duplicate release material"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[artifact],
            material_paths=[artifact, artifact],
            release_id="release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )
    with pytest.raises(ReleaseManifestError, match="not a regular file"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[tmp_path],
            release_id="release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )


def test_release_output_must_be_inside_root(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("data", encoding="utf-8")
    outside = tmp_path.parent / "outside-manifest.json"
    with pytest.raises(ReleaseManifestError, match="within the release root"):
        build_release_manifest(
            root=tmp_path,
            artefact_paths=[artifact],
            output_path=outside,
            release_id="release",
            software_version="0.3.0rc1",
            created_at="2026-07-19T00:00:00Z",
        )


def test_release_verifier_reports_structural_and_summary_failures(tmp_path: Path) -> None:
    _artifact, manifest = _release_fixture(tmp_path)

    invalid_collections = deepcopy(manifest)
    invalid_collections["artefacts"] = "not-a-list"
    invalid_collections["materials"] = "not-a-list"
    failures = verify_release_manifest(tmp_path, invalid_collections)
    assert "invalid manifest: artefacts must be a list" in failures
    assert "invalid manifest: materials must be a list" in failures

    empty = deepcopy(manifest)
    empty["artefacts"] = []
    assert "invalid manifest: artefacts must not be empty" in verify_release_manifest(
        tmp_path, empty
    )

    malformed = deepcopy(manifest)
    malformed["artefacts"] = [None]
    assert "invalid artefact entry at index 0" in verify_release_manifest(tmp_path, malformed)

    unsafe = deepcopy(manifest)
    unsafe["artefacts"][0]["path"] = "../outside.txt"  # type: ignore[index]
    assert "unsafe path: ../outside.txt" in verify_release_manifest(tmp_path, unsafe)

    duplicate = deepcopy(manifest)
    duplicate["artefacts"] = [
        deepcopy(manifest["artefacts"][0]),  # type: ignore[index]
        deepcopy(manifest["artefacts"][0]),  # type: ignore[index]
    ]
    assert any(
        "duplicate path" in failure for failure in verify_release_manifest(tmp_path, duplicate)
    )

    missing = deepcopy(manifest)
    missing["artefacts"][0]["path"] = "missing.txt"  # type: ignore[index]
    assert "missing: missing.txt" in verify_release_manifest(tmp_path, missing)

    summary = deepcopy(manifest)
    summary["summary"] = {"artefact_count": 0, "artefact_bytes": 0, "material_count": 1}
    failures = verify_release_manifest(tmp_path, summary)
    assert "summary artefact_count mismatch" in failures
    assert "summary artefact_bytes mismatch" in failures
    assert "summary material_count mismatch" in failures


def test_release_verifier_reports_symlink_size_and_clean_commit_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact, manifest = _release_fixture(tmp_path)
    size_changed = deepcopy(manifest)
    size_changed["artefacts"][0]["size_bytes"] = 999  # type: ignore[index]
    assert "size mismatch: result.txt" in verify_release_manifest(tmp_path, size_changed)

    target = tmp_path / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)
    symlink_manifest = deepcopy(manifest)
    symlink_manifest["artefacts"][0]["path"] = "link.txt"  # type: ignore[index]
    assert "symlink not permitted: link.txt" in verify_release_manifest(tmp_path, symlink_manifest)

    clean = deepcopy(manifest)
    clean["repository"] = {"commit": "1" * 40, "tree_state": "clean", "tag": None}
    monkeypatch.setattr(release_module, "_run_git", lambda _root, _args: "2" * 40)
    assert "repository commit differs from clean release manifest" in verify_release_manifest(
        tmp_path, clean
    )

    artifact.unlink()

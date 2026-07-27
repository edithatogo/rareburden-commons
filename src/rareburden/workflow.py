"""Fine-grained, retrospective workflow provenance.

A workflow run indexes immutable transformation-run records and derives the
causal graph from exact artefact identities.  It prevents a coarse workflow
claim from hiding which activity created each output or which upstream output
was actually consumed.
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from rareburden.provenance import canonical_json_bytes, content_id, sha256_file
from rareburden.transformation import verify_transformation_run


class WorkflowProvenanceError(ValueError):
    """Raised when workflow provenance is ambiguous, cyclic or inconsistent."""


@dataclass(frozen=True)
class TransformationRecordReference:
    """One immutable transformation record within a workflow."""

    record: Mapping[str, Any]
    path: str
    sha256: str
    size_bytes: int

    @classmethod
    def from_file(
        cls,
        record: Mapping[str, Any],
        path: Path,
        *,
        logical_path: str,
    ) -> TransformationRecordReference:
        """Create a reference and verify that disk content equals *record*."""
        safe = _safe_path(logical_path)
        if path.is_symlink() or not path.is_file():
            raise WorkflowProvenanceError(f"Transformation record is unavailable: {path}")
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise WorkflowProvenanceError(
                f"Cannot read transformation record {path}: {exc}"
            ) from exc
        if parsed != dict(record):
            raise WorkflowProvenanceError(
                f"Transformation record file differs from supplied record: {logical_path}"
            )
        if path.read_bytes() != canonical_json_bytes(record):
            raise WorkflowProvenanceError(
                f"Transformation record is not in canonical JSON form: {logical_path}"
            )
        digest, size = sha256_file(path)
        return cls(record=record, path=safe, sha256=digest, size_bytes=size)

    def as_dict(self) -> dict[str, Any]:
        """Return the immutable workflow-index representation."""
        return {
            "transformation_run_id": str(self.record["transformation_run_id"]),
            "activity_id": str(self.record["activity_id"]),
            "title": str(self.record["title"]),
            "status": str(self.record["status"]),
            "record_path": self.path,
            "record_sha256": self.sha256,
            "record_size_bytes": self.size_bytes,
        }


def _safe_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or value.startswith("./")
        or "\\" in value
        or any(ord(character) < 32 for character in value)
    ):
        raise WorkflowProvenanceError(f"Unsafe workflow path: {value!r}")
    return path.as_posix()


def _artifact_key(artifact: Mapping[str, Any]) -> tuple[str, str, int]:
    path = _safe_path(str(artifact.get("path", "")))
    digest = str(artifact.get("sha256", ""))
    size = artifact.get("size_bytes")
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise WorkflowProvenanceError(f"Invalid artefact SHA-256 for {path}")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise WorkflowProvenanceError(f"Invalid artefact size for {path}")
    return path, digest, size


def _artifact_projection(artifact: Mapping[str, Any]) -> dict[str, Any]:
    path, digest, size = _artifact_key(artifact)
    return {
        "path": path,
        "sha256": digest,
        "size_bytes": size,
        "media_type": str(artifact.get("media_type", "application/octet-stream")),
        "role": str(artifact.get("role", "unspecified")),
    }


def _topological_order(run_ids: Sequence[str], edges: Sequence[Mapping[str, Any]]) -> list[str]:
    adjacency: dict[str, set[str]] = {run_id: set() for run_id in run_ids}
    indegree = dict.fromkeys(run_ids, 0)
    for edge in edges:
        source = str(edge["from_run"])
        target = str(edge["to_run"])
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1
    ready = deque(sorted(run_id for run_id, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while ready:
        source = ready.popleft()
        order.append(source)
        for target in sorted(adjacency[source]):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    if len(order) != len(run_ids):
        raise WorkflowProvenanceError("Transformation dependency graph contains a cycle")
    return order


def _derive_graph(
    references: Sequence[TransformationRecordReference],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    producers: dict[str, tuple[str, Mapping[str, Any]]] = {}
    all_inputs: dict[str, Mapping[str, Any]] = {}
    all_outputs: dict[str, Mapping[str, Any]] = {}
    consumed_outputs: set[str] = set()
    edge_artifacts: dict[tuple[str, str], set[str]] = defaultdict(set)
    run_ids: list[str] = []

    for reference in references:
        run = reference.record
        run_id = str(run.get("transformation_run_id", ""))
        if not run_id or run_id in run_ids:
            raise WorkflowProvenanceError(f"Duplicate or missing transformation run id: {run_id!r}")
        run_ids.append(run_id)
        outputs = run.get("outputs")
        if not isinstance(outputs, list):
            raise WorkflowProvenanceError(f"Transformation {run_id} has invalid outputs")
        for output in outputs:
            if not isinstance(output, Mapping):
                raise WorkflowProvenanceError(f"Transformation {run_id} has malformed output")
            path, _, _ = _artifact_key(output)
            if path in producers:
                raise WorkflowProvenanceError(
                    f"Multiple transformation runs claim to produce {path}: "
                    f"{producers[path][0]}, {run_id}"
                )
            producers[path] = (run_id, output)
            all_outputs[path] = output

    for reference in references:
        run = reference.record
        run_id = str(run["transformation_run_id"])
        inputs = run.get("inputs")
        if not isinstance(inputs, list):
            raise WorkflowProvenanceError(f"Transformation {run_id} has invalid inputs")
        for input_artifact in inputs:
            if not isinstance(input_artifact, Mapping):
                raise WorkflowProvenanceError(f"Transformation {run_id} has malformed input")
            path, digest, size = _artifact_key(input_artifact)
            previous = all_inputs.get(path)
            if previous is not None:
                if _artifact_key(previous) != (path, digest, size):
                    raise WorkflowProvenanceError(f"Conflicting input identities for {path}")
                previous_media = str(
                    previous.get("media_type", "application/octet-stream")
                )
                current_media = str(
                    input_artifact.get("media_type", "application/octet-stream")
                )
                if previous_media != current_media:
                    raise WorkflowProvenanceError(
                        f"Conflicting input media types for {path}: "
                        f"{previous_media}, {current_media}"
                    )
                # An external artefact may serve different roles in different
                # transformations. Choose a stable projection so graph identity is
                # independent of transformation insertion order.
                all_inputs[path] = min(
                    (previous, input_artifact),
                    key=lambda item: (
                        str(item.get("media_type", "application/octet-stream")),
                        str(item.get("role", "unspecified")),
                    ),
                )
            else:
                all_inputs[path] = input_artifact
            producer = producers.get(path)
            if producer is None:
                continue
            producer_id, output_artifact = producer
            if producer_id == run_id:
                raise WorkflowProvenanceError(
                    f"Transformation {run_id} consumes its own output {path}"
                )
            if _artifact_key(output_artifact) != (path, digest, size):
                raise WorkflowProvenanceError(
                    f"Producer-consumer artefact identity mismatch for {path}"
                )
            consumed_outputs.add(path)
            edge_artifacts[(producer_id, run_id)].add(path)

    edges = [
        {
            "from_run": source,
            "to_run": target,
            "artifacts": sorted(paths),
        }
        for (source, target), paths in sorted(edge_artifacts.items())
    ]
    order = _topological_order(run_ids, edges)
    entry_inputs = [
        _artifact_projection(all_inputs[path]) for path in sorted(set(all_inputs) - set(producers))
    ]
    final_outputs = [
        _artifact_projection(all_outputs[path])
        for path in sorted(set(all_outputs) - consumed_outputs)
    ]
    return edges, entry_inputs, final_outputs, order


def build_workflow_run(
    *,
    workflow_id: str,
    title: str,
    prospective_plan: Mapping[str, Any],
    transformation_records: Sequence[TransformationRecordReference],
    created_at: str,
    assertions: Sequence[str] = (),
    limitations: Sequence[str] = (),
) -> dict[str, Any]:
    """Build a content-addressed workflow index from immutable activity records."""
    if not transformation_records:
        raise WorkflowProvenanceError("A workflow must contain at least one transformation run")
    edges, entry_inputs, final_outputs, order = _derive_graph(transformation_records)
    if not entry_inputs:
        raise WorkflowProvenanceError("A workflow must expose at least one external entry input")
    if not final_outputs:
        raise WorkflowProvenanceError("A workflow must expose at least one final output")
    runs = sorted(
        (reference.as_dict() for reference in transformation_records),
        key=lambda item: str(item["transformation_run_id"]),
    )
    core = {
        "workflow_id": workflow_id,
        "title": title,
        "created_at": created_at,
        "prospective_plan": json.loads(
            json.dumps(dict(prospective_plan), sort_keys=True, allow_nan=False)
        ),
        "runs": runs,
        "edges": edges,
        "topological_order": order,
        "entry_inputs": entry_inputs,
        "final_outputs": final_outputs,
        "assertions": sorted(set(assertions)),
        "limitations": sorted(set(limitations)),
    }
    return {
        "schema_version": "1.0.0",
        "workflow_run_id": content_id("workflow", core),
        **core,
    }


def verify_workflow_run(
    root: Path,
    workflow: Mapping[str, Any],
) -> list[str]:
    """Verify the workflow index, all transformation records and the derived DAG."""
    failures: list[str] = []
    identity_core = {
        key: value
        for key, value in workflow.items()
        if key not in {"schema_version", "workflow_run_id"}
    }
    try:
        expected_id = content_id("workflow", identity_core)
    except Exception as exc:
        failures.append(f"unable to recompute workflow identifier: {exc}")
    else:
        if workflow.get("workflow_run_id") != expected_id:
            failures.append("workflow run content identifier mismatch")

    root_resolved = root.expanduser().resolve()
    loaded_references: list[TransformationRecordReference] = []
    runs = workflow.get("runs")
    if not isinstance(runs, list) or not runs:
        return [*failures, "workflow runs must be a non-empty list"]
    for indexed in runs:
        if not isinstance(indexed, Mapping):
            failures.append("workflow contains a malformed run index")
            continue
        try:
            logical = _safe_path(str(indexed["record_path"]))
        except (KeyError, WorkflowProvenanceError) as exc:
            failures.append(str(exc))
            continue
        path = root_resolved / logical
        if path.is_symlink() or not path.is_file():
            failures.append(f"transformation record is missing or unsafe: {logical}")
            continue
        try:
            path.resolve().relative_to(root_resolved)
        except ValueError:
            failures.append(f"transformation record escapes workflow root: {logical}")
            continue
        digest, size = sha256_file(path)
        if digest != indexed.get("record_sha256"):
            failures.append(f"transformation record checksum mismatch: {logical}")
        if size != indexed.get("record_size_bytes"):
            failures.append(f"transformation record size mismatch: {logical}")
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"cannot parse transformation record {logical}: {exc}")
            continue
        if not isinstance(record, dict):
            failures.append(f"transformation record is not an object: {logical}")
            continue
        if record.get("transformation_run_id") != indexed.get("transformation_run_id"):
            failures.append(f"transformation run identifier mismatch: {logical}")
        failures.extend(
            f"{logical}: {failure}"
            for failure in verify_transformation_run(record, artefact_roots=[root_resolved])
        )
        loaded_references.append(
            TransformationRecordReference(
                record=record,
                path=logical,
                sha256=digest,
                size_bytes=size,
            )
        )

    if loaded_references:
        try:
            rebuilt = build_workflow_run(
                workflow_id=str(workflow.get("workflow_id", "")),
                title=str(workflow.get("title", "")),
                prospective_plan=dict(workflow.get("prospective_plan", {})),
                transformation_records=loaded_references,
                created_at=str(workflow.get("created_at", "")),
                assertions=[str(item) for item in workflow.get("assertions", [])],
                limitations=[str(item) for item in workflow.get("limitations", [])],
            )
        except (TypeError, WorkflowProvenanceError) as exc:
            failures.append(f"cannot rebuild workflow graph: {exc}")
        else:
            for field in (
                "workflow_run_id",
                "runs",
                "edges",
                "topological_order",
                "entry_inputs",
                "final_outputs",
            ):
                if workflow.get(field) != rebuilt.get(field):
                    failures.append(f"workflow derived field mismatch: {field}")
    return failures


__all__ = [
    "TransformationRecordReference",
    "WorkflowProvenanceError",
    "build_workflow_run",
    "verify_workflow_run",
]

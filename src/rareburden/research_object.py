"""Deterministic RO-Crate research objects for RareBurden releases.

The generated metadata follows RO-Crate 1.3 and the Process Run Crate 0.5
profile.  It preserves the distinction between prospective protocols and
retrospective execution, and can represent either one process or a fine-grained
multi-activity workflow graph.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, unquote, urlparse

from rareburden.provenance import atomic_write_json, content_id, sha256_file

RO_CRATE_CONTEXT = "https://w3id.org/ro/crate/1.3/context"
RO_CRATE_SPEC = "https://w3id.org/ro/crate/1.3"
PROCESS_RUN_CONTEXT = "https://w3id.org/ro/terms/workflow-run/context"
PROCESS_RUN_PROFILE = "https://w3id.org/ro/wfrun/process/0.5"
PROV_NAMESPACE = "http://www.w3.org/ns/prov#"


class ResearchObjectError(ValueError):
    """Raised when a research object is unsafe, incomplete or inconsistent."""


def _uri_path(path: str) -> str:
    pure = PurePosixPath(path)
    if (
        not path
        or pure.is_absolute()
        or ".." in pure.parts
        or path.startswith("./")
        or "\\" in path
        or any(ord(character) < 32 for character in path)
    ):
        raise ResearchObjectError(f"Unsafe RO-Crate path: {path!r}")
    return quote(pure.as_posix(), safe="/-._~")


def _ref(identifier: str) -> dict[str, str]:
    return {"@id": identifier}


def _as_ref_list(identifiers: Sequence[str]) -> list[dict[str, str]]:
    return [_ref(identifier) for identifier in identifiers]


def _artifact_identity(artifact: Mapping[str, Any]) -> tuple[str, str, int]:
    path = str(artifact["path"])
    digest = str(artifact["sha256"])
    size = artifact["size_bytes"]
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ResearchObjectError(f"Invalid content size for {path}")
    return path, digest, size


def _artifact_entity(
    artifact: Mapping[str, Any],
    *,
    generated_by: str | None,
) -> dict[str, Any]:
    path = str(artifact["path"])
    entity: dict[str, Any] = {
        "@id": _uri_path(path),
        "@type": "File",
        "name": PurePosixPath(path).name,
        "encodingFormat": str(artifact["media_type"]),
        "contentSize": str(artifact["size_bytes"]),
        "sha256": str(artifact["sha256"]),
        "description": f"RareBurden research artefact ({artifact['role']}).",
    }
    if generated_by is not None:
        entity["prov:wasGeneratedBy"] = _ref(generated_by)
    if artifact.get("licence_state"):
        entity["conditionsOfAccess"] = str(artifact["licence_state"])
    if artifact.get("source_release_id"):
        entity["identifier"] = str(artifact["source_release_id"])
    return entity


def _plan_entity(plan: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    identity = {
        "plan_id": str(plan["plan_id"]),
        "protocol": str(plan["protocol"]),
        "protocol_version": str(plan["protocol_version"]),
        "registered_at": plan.get("registered_at"),
        "preregistration": plan.get("preregistration"),
        "deviations": plan.get("deviations", []),
    }
    identifier = "#" + content_id("plan", identity, length=16)
    entity: dict[str, Any] = {
        "@id": identifier,
        "@type": "CreativeWork",
        "identifier": identity["plan_id"],
        "name": f"Prospective protocol {identity['plan_id']}",
        "version": identity["protocol_version"],
        "url": identity["protocol"],
    }
    if identity["preregistration"]:
        entity["sameAs"] = str(identity["preregistration"])
    if identity["registered_at"]:
        entity["dateCreated"] = str(identity["registered_at"])
    if identity["deviations"]:
        entity["description"] = "Recorded deviations: " + "; ".join(
            str(item) for item in identity["deviations"]
        )
    return identifier, entity


def _creator_entities(
    creators: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    entities: list[dict[str, Any]] = []
    refs: list[dict[str, str]] = []
    for creator in sorted(creators, key=lambda item: item["id"]):
        identifier = creator["id"]
        refs.append(_ref(identifier))
        entities.append(
            {
                "@id": identifier,
                "@type": creator.get("type", "Organization"),
                "name": creator["name"],
            }
        )
    return entities, refs


def _merge_artifacts(
    transformation_runs: Sequence[Mapping[str, Any]],
    additional_files: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, str], dict[str, str]]:
    artifacts: dict[str, Mapping[str, Any]] = {}
    generated_by: dict[str, str] = {}
    producer_by_path: dict[str, str] = {}
    for run in transformation_runs:
        run_id = str(run["transformation_run_id"])
        action_id = f"#{run_id}"
        for collection in ("inputs", "outputs"):
            for artifact in run[collection]:
                path, digest, size = _artifact_identity(artifact)
                previous = artifacts.get(path)
                if previous is not None and _artifact_identity(previous) != (path, digest, size):
                    raise ResearchObjectError(f"Conflicting artefact identities for {path}")
                artifacts[path] = artifact
                if collection == "outputs":
                    previous_producer = producer_by_path.get(path)
                    if previous_producer is not None and previous_producer != run_id:
                        raise ResearchObjectError(
                            f"Multiple transformation runs claim RO-Crate result {path}"
                        )
                    producer_by_path[path] = run_id
                    generated_by[path] = action_id
    for artifact in additional_files:
        path, digest, size = _artifact_identity(artifact)
        previous = artifacts.get(path)
        if previous is not None and _artifact_identity(previous) != (path, digest, size):
            raise ResearchObjectError(f"Conflicting additional artefact identity for {path}")
        artifacts[path] = artifact
    return artifacts, generated_by, producer_by_path


def _dependency_actions(
    run: Mapping[str, Any],
    producer_by_path: Mapping[str, str],
) -> list[str]:
    current = str(run["transformation_run_id"])
    upstream = {
        producer_by_path[str(item["path"])]
        for item in run["inputs"]
        if str(item["path"]) in producer_by_path and producer_by_path[str(item["path"])] != current
    }
    return [f"#{run_id}" for run_id in sorted(upstream)]


def build_workflow_run_crate(
    *,
    title: str,
    description: str,
    release_id: str,
    created_at: str,
    licence: str,
    transformation_runs: Sequence[Mapping[str, Any]],
    additional_files: Sequence[Mapping[str, Any]] = (),
    keywords: Sequence[str] = (),
    creators: Sequence[Mapping[str, str]] = (),
    workflow_run_id: str | None = None,
) -> dict[str, Any]:
    """Build deterministic RO-Crate metadata for one or more process runs."""
    if not transformation_runs:
        raise ResearchObjectError("At least one transformation run is required")
    run_ids = [str(run["transformation_run_id"]) for run in transformation_runs]
    if len(set(run_ids)) != len(run_ids):
        raise ResearchObjectError("Duplicate transformation run identifiers")

    artifacts, generated_by, producer_by_path = _merge_artifacts(
        transformation_runs, additional_files
    )
    all_file_ids = sorted(_uri_path(path) for path in artifacts)
    metadata_entity = {
        "@id": "ro-crate-metadata.json",
        "@type": "CreativeWork",
        "about": _ref("./"),
        "conformsTo": _ref(RO_CRATE_SPEC),
    }
    root_entity: dict[str, Any] = {
        "@id": "./",
        "@type": "Dataset",
        "identifier": release_id,
        "name": title,
        "description": description,
        "datePublished": created_at,
        "license": _ref(licence),
        "conformsTo": _ref(PROCESS_RUN_PROFILE),
        "hasPart": _as_ref_list(all_file_ids),
        "keywords": sorted(set(keywords)),
    }
    if workflow_run_id is not None:
        root_entity["identifier"] = [release_id, workflow_run_id]

    creator_entities, creator_refs = _creator_entities(creators)
    if creator_refs:
        root_entity["creator"] = creator_refs

    plan_entities: dict[str, dict[str, Any]] = {}
    software_entities: list[dict[str, Any]] = []
    action_entities: list[dict[str, Any]] = []
    mention_ids: list[str] = []
    for run in sorted(transformation_runs, key=lambda item: str(item["transformation_run_id"])):
        run_id = str(run["transformation_run_id"])
        action_id = f"#{run_id}"
        plan_id, plan_entity = _plan_entity(run["prospective_plan"])
        plan_entities[plan_id] = plan_entity
        software_id = f"#software-{run_id}"
        software = run["software"]
        environment = run["environment"]
        software_entity: dict[str, Any] = {
            "@id": software_id,
            "@type": ["SoftwareApplication", "SoftwareSourceCode"],
            "name": str(software["name"]),
            "softwareVersion": str(software["version"]),
            "runtimePlatform": str(environment["python"]["version"]),
            "identifier": str(software.get("git_commit") or "uncommitted-or-unavailable"),
        }
        software_entities.append(software_entity)
        status = str(run["status"])
        action_status = {
            "completed": "https://schema.org/CompletedActionStatus",
            "failed": "https://schema.org/FailedActionStatus",
            "cancelled": "https://schema.org/FailedActionStatus",
        }[status]
        action: dict[str, Any] = {
            "@id": action_id,
            "@type": "CreateAction",
            "name": str(run["title"]),
            "description": "Argument vector: "
            + " ".join(str(part) for part in software["command"]),
            "actionStatus": _ref(action_status),
            "startTime": str(run["execution"]["started_at"]),
            "endTime": str(run["execution"]["ended_at"]),
            "instrument": _ref(software_id),
            "object": _as_ref_list([_uri_path(str(item["path"])) for item in run["inputs"]]),
            "result": _as_ref_list([_uri_path(str(item["path"])) for item in run["outputs"]]),
            "prov:hadPlan": _ref(plan_id),
        }
        upstream = _dependency_actions(run, producer_by_path)
        if upstream:
            action["prov:wasInformedBy"] = _as_ref_list(upstream)
        if creator_refs:
            action["agent"] = creator_refs
        action_entities.append(action)
        mention_ids.extend((action_id, plan_id))
    root_entity["mentions"] = _as_ref_list(sorted(set(mention_ids)))

    file_entities = [
        _artifact_entity(artifact, generated_by=generated_by.get(path))
        for path, artifact in sorted(artifacts.items())
    ]
    profile_entities = [
        {
            "@id": PROCESS_RUN_PROFILE,
            "@type": "CreativeWork",
            "name": "Process Run Crate",
            "version": "0.5",
        },
        {
            "@id": RO_CRATE_SPEC,
            "@type": "CreativeWork",
            "name": "RO-Crate Metadata Specification",
            "version": "1.3",
        },
    ]
    graph = [
        metadata_entity,
        root_entity,
        *profile_entities,
        *plan_entities.values(),
        *software_entities,
        *action_entities,
        *creator_entities,
        *file_entities,
    ]
    graph.sort(key=lambda entity: str(entity["@id"]))
    return {
        "@context": [
            RO_CRATE_CONTEXT,
            PROCESS_RUN_CONTEXT,
            {"prov": PROV_NAMESPACE},
        ],
        "@graph": graph,
    }


def build_process_run_crate(
    *,
    title: str,
    description: str,
    release_id: str,
    created_at: str,
    licence: str,
    transformation_run: Mapping[str, Any],
    additional_files: Sequence[Mapping[str, Any]] = (),
    keywords: Sequence[str] = (),
    creators: Sequence[Mapping[str, str]] = (),
) -> dict[str, Any]:
    """Build a single-process crate; retained as a compatibility wrapper."""
    return build_workflow_run_crate(
        title=title,
        description=description,
        release_id=release_id,
        created_at=created_at,
        licence=licence,
        transformation_runs=[transformation_run],
        additional_files=additional_files,
        keywords=keywords,
        creators=creators,
    )


def _is_external_identifier(identifier: str) -> bool:
    parsed = urlparse(identifier)
    return bool(parsed.scheme and parsed.scheme not in {"file"})


def _entity_index(crate: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    failures: list[str] = []
    graph = crate.get("@graph")
    if not isinstance(graph, list):
        return {}, ["@graph must be a list"]
    index: dict[str, Mapping[str, Any]] = {}
    for position, entity in enumerate(graph):
        if not isinstance(entity, Mapping) or not isinstance(entity.get("@id"), str):
            failures.append(f"invalid entity at graph index {position}")
            continue
        identifier = str(entity["@id"])
        if identifier in index:
            failures.append(f"duplicate entity identifier: {identifier}")
            continue
        index[identifier] = entity
    return index, failures


def _reference_ids(value: Any) -> list[str]:
    if isinstance(value, Mapping) and isinstance(value.get("@id"), str):
        return [str(value["@id"])]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_reference_ids(item))
        return result
    return []


def _verify_actions(
    index: Mapping[str, Mapping[str, Any]],
    actions: Sequence[Mapping[str, Any]],
) -> list[str]:
    failures: list[str] = []
    result_producers: dict[str, str] = {}
    action_ids = {str(action["@id"]) for action in actions}
    for action in actions:
        action_id = str(action["@id"])
        for property_name in ("instrument", "object", "result", "startTime", "endTime"):
            if property_name not in action:
                failures.append(f"CreateAction is missing {property_name}")
        objects = _reference_ids(action.get("object"))
        results = _reference_ids(action.get("result"))
        if not objects or not results:
            failures.append("CreateAction must identify both inputs and outputs")
        instrument_ids = _reference_ids(action.get("instrument"))
        for identifier in [*objects, *results, *instrument_ids]:
            if identifier not in index:
                failures.append(f"CreateAction {action_id} references missing entity {identifier}")
        for identifier in results:
            previous = result_producers.get(identifier)
            if previous is not None and previous != action_id:
                failures.append(f"file {identifier} is a result of multiple CreateActions")
            result_producers[identifier] = action_id
        for upstream in _reference_ids(action.get("prov:wasInformedBy")):
            if upstream not in action_ids:
                failures.append(f"CreateAction {action_id} references unknown upstream {upstream}")
    for file_id, producer in result_producers.items():
        entity = index.get(file_id)
        if entity is not None and _reference_ids(entity.get("prov:wasGeneratedBy")) != [producer]:
            failures.append(f"file {file_id} does not identify its producing CreateAction")
    return failures


def verify_process_run_crate(crate_root: Path, crate: Mapping[str, Any]) -> list[str]:
    """Verify profile structure, action closure and all in-crate file identities."""
    failures: list[str] = []
    root = crate_root.expanduser().resolve()
    context = crate.get("@context")
    if not isinstance(context, list) or RO_CRATE_CONTEXT not in context:
        failures.append("RO-Crate 1.3 context is missing")
    if not isinstance(context, list) or PROCESS_RUN_CONTEXT not in context:
        failures.append("Process Run context is missing")

    index, index_failures = _entity_index(crate)
    failures.extend(index_failures)
    metadata = index.get("ro-crate-metadata.json")
    root_entity = index.get("./")
    if metadata is None:
        failures.append("metadata descriptor entity is missing")
    elif metadata.get("about") != _ref("./") or metadata.get("conformsTo") != _ref(RO_CRATE_SPEC):
        failures.append("metadata descriptor does not identify an RO-Crate 1.3 root")
    if root_entity is None:
        failures.append("root dataset entity is missing")
    elif root_entity.get("conformsTo") != _ref(PROCESS_RUN_PROFILE):
        failures.append("root dataset does not declare Process Run Crate 0.5")

    actions = [entity for entity in index.values() if entity.get("@type") == "CreateAction"]
    if not actions:
        failures.append("at least one CreateAction is required")
    else:
        failures.extend(_verify_actions(index, actions))

    for identifier, entity in index.items():
        entity_type = entity.get("@type")
        types = entity_type if isinstance(entity_type, list) else [entity_type]
        if "File" not in types:
            continue
        if _is_external_identifier(identifier) or identifier.startswith("#"):
            continue
        relative_text = unquote(identifier)
        try:
            safe_path = _uri_path(relative_text)
        except ResearchObjectError as exc:
            failures.append(str(exc))
            continue
        if safe_path != identifier:
            failures.append(f"non-canonical encoded file identifier: {identifier}")
            continue
        path = root / relative_text
        if path.is_symlink():
            failures.append(f"symlink file entity is not permitted: {relative_text}")
            continue
        try:
            path.resolve().relative_to(root)
        except ValueError:
            failures.append(f"file entity escapes crate root: {relative_text}")
            continue
        if not path.is_file():
            failures.append(f"file entity is missing: {relative_text}")
            continue
        digest, size = sha256_file(path)
        if digest != entity.get("sha256"):
            failures.append(f"file checksum mismatch: {relative_text}")
        if str(size) != str(entity.get("contentSize")):
            failures.append(f"file size mismatch: {relative_text}")

    if root_entity is not None:
        part_ids = set(_reference_ids(root_entity.get("hasPart")))
        file_ids: set[str] = set()
        for identifier, entity in index.items():
            entity_type = entity.get("@type")
            types = entity_type if isinstance(entity_type, list) else [entity_type]
            if "File" in types:
                file_ids.add(identifier)
        if part_ids != file_ids:
            failures.append("root hasPart does not exactly enumerate file entities")
    return failures


def write_process_run_crate(path: Path, crate: Mapping[str, Any]) -> None:
    """Write canonical RO-Crate JSON-LD metadata atomically."""
    atomic_write_json(path, dict(crate))


__all__ = [
    "PROCESS_RUN_CONTEXT",
    "PROCESS_RUN_PROFILE",
    "RO_CRATE_CONTEXT",
    "RO_CRATE_SPEC",
    "ResearchObjectError",
    "build_process_run_crate",
    "build_workflow_run_crate",
    "verify_process_run_crate",
    "write_process_run_crate",
]

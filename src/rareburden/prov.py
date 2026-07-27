"""Interoperable W3C PROV-O JSON-LD exports for RareBurden workflow evidence.

The native transformation and workflow records are the normative, content-addressed
records used for verification.  This module projects those records into PROV-O so that
external repositories and provenance tooling can inspect activities, entities, agents,
plans, derivations, and causal ordering without understanding RareBurden-specific JSON.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

from rareburden.provenance import canonical_json_bytes, content_id

PROV_NAMESPACE = "http://www.w3.org/ns/prov#"
SCHEMA_NAMESPACE = "https://schema.org/"
RAREBURDEN_NAMESPACE = "https://rareburden.org/ns#"


class ProvBundleError(ValueError):
    """Raised when an interoperable provenance bundle cannot be built safely."""


def _ref(identifier: str) -> dict[str, str]:
    return {"@id": identifier}


def _refs(identifiers: Sequence[str]) -> list[dict[str, str]]:
    return [_ref(identifier) for identifier in sorted(set(identifiers))]


def _artifact_id(artifact: Mapping[str, Any]) -> str:
    path = str(artifact.get("path", ""))
    digest = str(artifact.get("sha256", ""))
    if not path or len(digest) != 64:
        raise ProvBundleError("Every provenance artefact requires a logical path and SHA-256")
    path_digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]
    return f"urn:rareburden:artifact:sha256:{digest}:{path_digest}"


def _activity_id(run_id: str) -> str:
    if not run_id.startswith("run-"):
        raise ProvBundleError(f"Invalid transformation run identifier: {run_id!r}")
    return f"urn:rareburden:activity:{run_id}"


def _plan_id(plan: Mapping[str, Any]) -> str:
    return "urn:rareburden:plan:" + content_id("plan", dict(plan)).removeprefix("plan-")


def _agent_id(agent: Mapping[str, Any]) -> str:
    supplied = str(agent.get("id", "")).strip()
    if supplied.startswith("https://") or supplied.startswith("urn:"):
        return supplied
    identity = {
        "id": supplied,
        "name": str(agent.get("name", "")),
        "role": str(agent.get("role", "")),
    }
    return "urn:rareburden:agent:" + content_id("agent", identity).removeprefix("agent-")


def _software_id(run: Mapping[str, Any]) -> str:
    software = run.get("software")
    if not isinstance(software, Mapping):
        raise ProvBundleError("Transformation run lacks software identity")
    identity = {
        "name": software.get("name"),
        "version": software.get("version"),
        "git_commit": software.get("git_commit"),
        "entry_point": software.get("entry_point"),
    }
    return "urn:rareburden:software:" + content_id("software", identity).removeprefix("software-")


def _entity(artifact: Mapping[str, Any]) -> dict[str, Any]:
    identifier = _artifact_id(artifact)
    value: dict[str, Any] = {
        "@id": identifier,
        "@type": ["prov:Entity", "schema:MediaObject"],
        "schema:name": str(artifact["path"]),
        "schema:contentSize": int(artifact["size_bytes"]),
        "schema:encodingFormat": str(artifact["media_type"]),
        "rb:logicalPath": str(artifact["path"]),
        "rb:sha256": str(artifact["sha256"]),
        "rb:role": str(artifact["role"]),
    }
    for field in ("source_release_id", "acquisition_manifest_id", "licence_state"):
        if artifact.get(field) is not None:
            value[f"rb:{field}"] = str(artifact[field])
    return value


def _extract_refs(value: Any) -> list[str]:
    if isinstance(value, Mapping) and isinstance(value.get("@id"), str):
        return [str(value["@id"])]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_extract_refs(item))
        return result
    return []


def build_prov_bundle(
    *,
    workflow: Mapping[str, Any],
    transformation_runs: Sequence[Mapping[str, Any]],
    release_id: str,
    title: str,
    generated_at: str,
) -> dict[str, Any]:
    """Project a verified workflow into deterministic PROV-O JSON-LD.

    Native transformation records remain normative.  This bundle is an interoperable
    projection and therefore carries the native workflow identifier and record IDs.
    """
    if not transformation_runs:
        raise ProvBundleError("At least one transformation run is required")
    workflow_run_id = str(workflow.get("workflow_run_id", ""))
    if not workflow_run_id.startswith("workflow-"):
        raise ProvBundleError("Workflow provenance requires a valid workflow_run_id")

    indexed_runs: dict[str, Mapping[str, Any]] = {}
    entities: dict[str, dict[str, Any]] = {}
    producer_by_artifact: dict[str, str] = {}
    agents: dict[str, dict[str, Any]] = {}
    software_agents: dict[str, dict[str, Any]] = {}
    plans: dict[str, dict[str, Any]] = {}

    for run in transformation_runs:
        run_id = str(run.get("transformation_run_id", ""))
        if not run_id or run_id in indexed_runs:
            raise ProvBundleError(f"Duplicate or missing transformation run id: {run_id!r}")
        indexed_runs[run_id] = run
        plan = run.get("prospective_plan")
        if not isinstance(plan, Mapping):
            raise ProvBundleError(f"Transformation {run_id} lacks a prospective plan")
        plan_identifier = _plan_id(plan)
        plans.setdefault(
            plan_identifier,
            {
                "@id": plan_identifier,
                "@type": ["prov:Plan", "schema:CreativeWork"],
                "schema:name": str(plan.get("plan_id", "prospective plan")),
                "schema:version": str(plan.get("protocol_version", "")),
                "schema:url": str(plan.get("protocol", "")),
                "rb:registeredAt": plan.get("registered_at"),
                "rb:preregistration": plan.get("preregistration"),
                "rb:declaredDeviations": sorted(str(item) for item in plan.get("deviations", [])),
            },
        )
        software = run.get("software")
        if not isinstance(software, Mapping):
            raise ProvBundleError(f"Transformation {run_id} lacks software metadata")
        software_identifier = _software_id(run)
        software_agents.setdefault(
            software_identifier,
            {
                "@id": software_identifier,
                "@type": ["prov:SoftwareAgent", "schema:SoftwareApplication"],
                "schema:name": str(software.get("name", "")),
                "schema:softwareVersion": str(software.get("version", "")),
                "rb:entryPoint": str(software.get("entry_point", "")),
                "rb:gitCommit": software.get("git_commit"),
                "rb:gitTreeState": str(software.get("git_tree_state", "")),
            },
        )
        for agent in run.get("agents", []):
            if not isinstance(agent, Mapping):
                raise ProvBundleError(f"Transformation {run_id} has malformed agent metadata")
            identifier = _agent_id(agent)
            entity: dict[str, Any] = {
                "@id": identifier,
                "@type": "prov:Agent",
                "schema:name": str(agent.get("name", "")),
                "rb:role": str(agent.get("role", "")),
            }
            if agent.get("orcid"):
                entity["schema:identifier"] = str(agent["orcid"])
            if agent.get("ror"):
                entity["schema:affiliation"] = _ref(str(agent["ror"]))
            agents.setdefault(identifier, entity)
        for field in ("inputs", "outputs"):
            artefacts = run.get(field)
            if not isinstance(artefacts, list) or not artefacts:
                raise ProvBundleError(f"Transformation {run_id} requires non-empty {field}")
            for artefact in artefacts:
                if not isinstance(artefact, Mapping):
                    raise ProvBundleError(f"Transformation {run_id} has malformed {field}")
                entity = _entity(artefact)
                identifier = str(entity["@id"])
                previous = entities.get(identifier)
                if previous is not None:
                    for key in ("rb:logicalPath", "rb:sha256", "schema:contentSize"):
                        if previous.get(key) != entity.get(key):
                            raise ProvBundleError(
                                f"Conflicting identities for provenance entity {identifier}"
                            )
                else:
                    entities[identifier] = entity
                if field == "outputs":
                    if identifier in producer_by_artifact:
                        raise ProvBundleError(
                            f"Multiple runs generate provenance entity {identifier}"
                        )
                    producer_by_artifact[identifier] = run_id

    edge_upstream: dict[str, set[str]] = {run_id: set() for run_id in indexed_runs}
    for edge in workflow.get("edges", []):
        if not isinstance(edge, Mapping):
            raise ProvBundleError("Workflow contains a malformed edge")
        source = str(edge.get("from_run", ""))
        target = str(edge.get("to_run", ""))
        if source not in indexed_runs or target not in indexed_runs:
            raise ProvBundleError("Workflow edge refers to an unknown transformation run")
        edge_upstream[target].add(source)

    activities: list[dict[str, Any]] = []
    for run_id, run in sorted(indexed_runs.items()):
        inputs = [_artifact_id(item) for item in run["inputs"]]
        outputs = [_artifact_id(item) for item in run["outputs"]]
        plan_identifier = _plan_id(run["prospective_plan"])
        software_identifier = _software_id(run)
        associated = [software_identifier]
        associated.extend(
            _agent_id(agent) for agent in run.get("agents", []) if isinstance(agent, Mapping)
        )
        activity: dict[str, Any] = {
            "@id": _activity_id(run_id),
            "@type": ["prov:Activity", "schema:CreateAction"],
            "schema:name": str(run.get("title", "")),
            "prov:startedAtTime": str(run["execution"]["started_at"]),
            "prov:endedAtTime": str(run["execution"]["ended_at"]),
            "prov:used": _refs(inputs),
            "prov:generated": _refs(outputs),
            "prov:hadPlan": _ref(plan_identifier),
            "prov:wasAssociatedWith": _refs(associated),
            "rb:activityId": str(run.get("activity_id", "")),
            "rb:status": str(run.get("status", "")),
            "rb:nativeRecordId": run_id,
        }
        if edge_upstream[run_id]:
            activity["prov:wasInformedBy"] = _refs(
                [_activity_id(item) for item in edge_upstream[run_id]]
            )
        activities.append(activity)
        for output_id in outputs:
            entity = entities[output_id]
            entity["prov:wasGeneratedBy"] = _ref(_activity_id(run_id))
            entity["prov:wasDerivedFrom"] = _refs(inputs)

    bundle_core = {
        "release_id": release_id,
        "workflow_run_id": workflow_run_id,
        "generated_at": generated_at,
        "activity_ids": sorted(indexed_runs),
        "artifact_ids": sorted(entities),
    }
    bundle_id = "urn:rareburden:provenance:" + content_id("prov", bundle_core).removeprefix("prov-")
    bundle_entity = {
        "@id": bundle_id,
        "@type": ["prov:Bundle", "schema:Dataset"],
        "schema:name": title,
        "schema:dateCreated": generated_at,
        "schema:identifier": release_id,
        "rb:nativeWorkflowRunId": workflow_run_id,
        "prov:hadMember": _refs(
            [
                *entities.keys(),
                *(_activity_id(run_id) for run_id in indexed_runs),
                *plans.keys(),
                *agents.keys(),
                *software_agents.keys(),
            ]
        ),
    }
    graph = [
        bundle_entity,
        *plans.values(),
        *agents.values(),
        *software_agents.values(),
        *activities,
        *entities.values(),
    ]
    graph.sort(key=lambda entity: str(entity["@id"]))
    payload = {
        "@context": {
            "prov": PROV_NAMESPACE,
            "schema": SCHEMA_NAMESPACE,
            "rb": RAREBURDEN_NAMESPACE,
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "prov:startedAtTime": {"@type": "xsd:dateTime"},
            "prov:endedAtTime": {"@type": "xsd:dateTime"},
            "schema:dateCreated": {"@type": "xsd:dateTime"},
        },
        "@id": bundle_id,
        "@graph": graph,
    }
    return {
        **payload,
        "rb:canonicalDigest": hashlib.sha256(canonical_json_bytes(payload)).hexdigest(),
    }


def verify_prov_bundle(
    bundle: Mapping[str, Any],
    *,
    workflow: Mapping[str, Any],
    transformation_runs: Sequence[Mapping[str, Any]],
) -> list[str]:
    """Structurally verify a PROV projection against native workflow evidence."""
    failures: list[str] = []
    canonical_payload = {
        key: value for key, value in bundle.items() if key != "rb:canonicalDigest"
    }
    expected_digest = hashlib.sha256(canonical_json_bytes(canonical_payload)).hexdigest()
    if bundle.get("rb:canonicalDigest") != expected_digest:
        failures.append("PROV bundle canonical digest mismatch")
    context = bundle.get("@context")
    if not isinstance(context, Mapping) or context.get("prov") != PROV_NAMESPACE:
        failures.append("PROV-O context is missing or incorrect")
    graph = bundle.get("@graph")
    if not isinstance(graph, list):
        return [*failures, "PROV bundle @graph must be a list"]
    index: dict[str, Mapping[str, Any]] = {}
    for position, entity in enumerate(graph):
        if not isinstance(entity, Mapping) or not isinstance(entity.get("@id"), str):
            failures.append(f"invalid PROV entity at graph index {position}")
            continue
        identifier = str(entity["@id"])
        if identifier in index:
            failures.append(f"duplicate PROV identifier: {identifier}")
        index[identifier] = entity

    expected_run_ids = {str(run.get("transformation_run_id", "")) for run in transformation_runs}
    expected_activities = {_activity_id(run_id) for run_id in expected_run_ids if run_id}
    actual_activities = {
        identifier
        for identifier, entity in index.items()
        if "prov:Activity"
        in (entity.get("@type") if isinstance(entity.get("@type"), list) else [entity.get("@type")])
    }
    if actual_activities != expected_activities:
        failures.append("PROV activities do not exactly match transformation runs")

    expected_artifacts: set[str] = set()
    for run in transformation_runs:
        run_id = str(run.get("transformation_run_id", ""))
        activity = index.get(_activity_id(run_id))
        if activity is None:
            continue
        expected_inputs = {_artifact_id(item) for item in run.get("inputs", [])}
        expected_outputs = {_artifact_id(item) for item in run.get("outputs", [])}
        expected_artifacts.update(expected_inputs | expected_outputs)
        if set(_extract_refs(activity.get("prov:used"))) != expected_inputs:
            failures.append(f"PROV used relation mismatch for {run_id}")
        if set(_extract_refs(activity.get("prov:generated"))) != expected_outputs:
            failures.append(f"PROV generated relation mismatch for {run_id}")
        for output_id in expected_outputs:
            entity = index.get(output_id)
            if entity is None:
                failures.append(f"PROV output entity is missing: {output_id}")
                continue
            if _extract_refs(entity.get("prov:wasGeneratedBy")) != [_activity_id(run_id)]:
                failures.append(f"PROV generation relation mismatch for {output_id}")
            if set(_extract_refs(entity.get("prov:wasDerivedFrom"))) != expected_inputs:
                failures.append(f"PROV derivation relation mismatch for {output_id}")

    actual_artifacts = {
        identifier
        for identifier, entity in index.items()
        if "prov:Entity"
        in (entity.get("@type") if isinstance(entity.get("@type"), list) else [entity.get("@type")])
    }
    if actual_artifacts != expected_artifacts:
        failures.append("PROV entities do not exactly match workflow artefacts")

    expected_upstream: dict[str, set[str]] = {run_id: set() for run_id in expected_run_ids}
    for edge in workflow.get("edges", []):
        if isinstance(edge, Mapping):
            expected_upstream.setdefault(str(edge.get("to_run", "")), set()).add(
                str(edge.get("from_run", ""))
            )
    for run_id, upstream in expected_upstream.items():
        activity = index.get(_activity_id(run_id))
        if activity is None:
            continue
        actual = {
            identifier.removeprefix("urn:rareburden:activity:")
            for identifier in _extract_refs(activity.get("prov:wasInformedBy"))
        }
        if actual != upstream:
            failures.append(f"PROV informed-by relation mismatch for {run_id}")

    local_identifiers = set(index)
    for identifier, entity in index.items():
        for key, value in entity.items():
            if key.startswith("prov:"):
                for referenced in _extract_refs(value):
                    if (
                        referenced.startswith("urn:rareburden:")
                        and referenced not in local_identifiers
                    ):
                        failures.append(
                            f"dangling PROV reference from {identifier} to {referenced}"
                        )
    return sorted(set(failures))


__all__ = [
    "PROV_NAMESPACE",
    "RAREBURDEN_NAMESPACE",
    "SCHEMA_NAMESPACE",
    "ProvBundleError",
    "build_prov_bundle",
    "verify_prov_bundle",
]

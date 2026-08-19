#!/usr/bin/env python3
"""Validate bounded HPO release and translation-history inventories."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def validate(releases_path: Path, translations_path: Path) -> dict[str, object]:
    releases = json.loads(releases_path.read_text(encoding="utf-8"))
    translations = json.loads(translations_path.read_text(encoding="utf-8"))
    tags = [item["tag"] for item in releases["releases"]]
    if len(tags) != len(set(tags)) or releases["observed_release_count"] != len(tags):
        raise ValueError("HPO release inventory is inconsistent or contains duplicate tags")
    assets = [asset for item in releases["releases"] for asset in item["assets"]]
    keys = [(asset["release_tag"], asset["name"]) for asset in assets]
    if len(keys) != len(set(keys)) or releases["observed_asset_count"] != len(assets):
        raise ValueError("HPO asset inventory is inconsistent or contains duplicates")
    if any(asset["archive_route"] != "metadata_only" for asset in assets):
        raise ValueError("HPO bytes must remain metadata-only until exact asset rights close")
    existing = set(releases["already_archived_release_tags"])
    missing = set(releases["observed_release_tags_not_in_existing_manifest"])
    if existing & missing or existing | missing != set(tags):
        raise ValueError("HPO existing/missing release partition is inconsistent")
    if translations["byte_archive_route"] != "disabled_pending_exact_licence":
        raise ValueError("translation bytes must fail closed without an exact licence")
    languages = translations["observed_language_codes"]
    if languages != sorted(set(languages)):
        raise ValueError("translation languages must be sorted and unique")
    return {
        "hpo_releases": len(tags),
        "hpo_assets": len(assets),
        "historical_release_gaps": len(missing),
        "translation_languages": len(languages),
        "translation_commits_observed": translations["observed_commit_count"],
    }


def publish_metadata(
    releases_path: Path, translations_path: Path, repo_id: str
) -> dict[str, object]:
    """Publish only validated factual metadata to an existing public dataset."""
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    summary = validate(releases_path, translations_path)
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required")
    api = HfApi(token=token)
    if api.dataset_info(repo_id).private:
        raise RuntimeError("HPO metadata destination must be public")
    paths = []
    for source in (releases_path, translations_path):
        destination = f"registry/hpo/{source.name}"
        api.upload_file(
            path_or_fileobj=str(source),
            path_in_repo=destination,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Archive bounded HPO metadata: {source.name}",
        )
        paths.append(destination)
    return {**summary, "repository": repo_id, "published_paths": paths, "raw_bytes": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--releases", type=Path, required=True)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--publish-public-metadata", action="store_true")
    parser.add_argument("--repo-id", default="edithatogo/dataset-estate-registry")
    args = parser.parse_args()
    result = (
        publish_metadata(args.releases, args.translations, args.repo_id)
        if args.publish_public_metadata
        else validate(args.releases, args.translations)
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

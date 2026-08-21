PYTHON ?= python
UV ?= uv
VERSION := $(shell $(PYTHON) -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
WHEEL := dist/rareburden-$(subst -,_,$(VERSION))-py3-none-any.whl
SDIST := dist/rareburden-$(VERSION).tar.gz

.PHONY: install sync validate validate-catalog validate-roadmap validate-landscape \
	test coverage critical-coverage typecheck lint format-check links safety compile schemas \
	workflows lock requirements runtime-assets runtime-assets-check release-identity \
	validation-artifacts validation-artifacts-check \
	downstream-preparation-check \
	single-owner-agent-governance-check \
	track-008-freeze-readiness-check \
	track-009-freeze-readiness-check \
	track-009-source-profile-role-check \
	track-010-alpha-freeze-readiness-check \
	track-010-candidate-containment-check \
	track-016-production-release-readiness-check \
	mutation mutation-score \
	reproducibility burden-benchmark node-bundle-check release-attestation-verify \
	offline-node-install offline-node-ci build package-check installed-package-check sbom external-receipt-check qualifying-receipts-check package-size-check check ci release-check clean

package-size-check: build
	PYTHONPATH=src:. $(PYTHON) scripts/check_package_size_policy.py \
		docs/track-016-package-size-policy.yml --root .

mutation:
	$(PYTHON) -m mutmut run
	$(PYTHON) -m mutmut export-cicd-stats
	$(MAKE) mutation-score

mutation-score:
	PYTHONPATH=src:. $(PYTHON) scripts/check_mutation_score.py \
		mutants/mutmut-cicd-stats.json --minimum 65

external-receipt-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_external_receipt.py \
		docs/external-gate-receipt-template.yml

qualifying-receipts-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_qualifying_receipts_register.py \
		docs/qualifying-receipts-register.yml

downstream-preparation-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_downstream_preparation.py \
		docs/downstream-bounded-preparation-plan-2026-08-03.yml --root .

single-owner-agent-governance-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_single_owner_agent_governance.py \
		docs/single-owner-agent-governance.yml --root .

track-008-freeze-readiness-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_track_008_freeze_readiness.py \
		docs/track-008-freeze-readiness-2026-08-21.yml --root .

track-009-freeze-readiness-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_track_009_freeze_readiness.py \
		docs/track-009-freeze-readiness-2026-08-21.yml --root .

track-009-source-profile-role-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_track009_source_profile_role.py \
		examples/ledger/source-profile-role-structural-synthetic.yml \
		--schema schemas/source-profile-role-structural-assessment.schema.json --root .

track-010-alpha-freeze-readiness-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_track_010_alpha_freeze_readiness.py \
		docs/track-010-alpha-freeze-readiness-2026-08-21.yml --root .

track-010-candidate-containment-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_track010_candidate_containment.py --root .

track-016-production-release-readiness-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_track_016_production_release_readiness.py \
		docs/track-016-production-release-readiness-2026-08-21.yml --root .

install:
	$(UV) sync --frozen --extra dev

sync:
	$(UV) sync --frozen --extra dev

validate:
	PYTHONPATH=src:. $(PYTHON) -m rareburden validate-programme

validate-catalog:
	PYTHONPATH=src:. $(PYTHON) -m rareburden validate-catalog

validate-roadmap:
	PYTHONPATH=src:. $(PYTHON) -m rareburden validate-roadmap

validate-landscape:
	PYTHONPATH=src:. $(PYTHON) -m rareburden validate-landscape

test:
	PYTHONPATH=src:. $(PYTHON) -m pytest

coverage:
	PYTHONPATH=src:. $(PYTHON) -m pytest --cov=rareburden --cov-branch \
		--cov-report=term-missing --cov-report=json:coverage.json \
		--cov-report=xml:coverage.xml --junitxml=junit.xml

critical-coverage:
	PYTHONPATH=src:. $(PYTHON) scripts/check_critical_coverage.py coverage.json

typecheck:
	$(PYTHON) -m mypy src/rareburden

lint:
	$(PYTHON) -m ruff check .

format-check:
	$(PYTHON) -m ruff format --check .

links:
	PYTHONPATH=src:. $(PYTHON) scripts/check_markdown_links.py

safety:
	PYTHONPATH=src:. $(PYTHON) scripts/check_repository_safety.py

compile:
	$(PYTHON) -m compileall -q src scripts

schemas:
	PYTHONPATH=src:. $(PYTHON) scripts/check_schemas.py

workflows:
	PYTHONPATH=src:. $(PYTHON) scripts/check_github_workflows.py

lock:
	PYTHONPATH=src:. $(PYTHON) scripts/check_lockfile.py uv.lock --pyproject pyproject.toml

requirements:
	PYTHONPATH=src:. $(PYTHON) scripts/check_requirements_exports.py --root .

runtime-assets:
	PYTHONPATH=src:. $(PYTHON) scripts/sync_runtime_assets.py --root .

runtime-assets-check:
	PYTHONPATH=src:. $(PYTHON) scripts/check_runtime_assets.py --root .

validation-artifacts:
	PYTHONPATH=src:. $(PYTHON) scripts/sync_validation_artifacts.py --root . --write

validation-artifacts-check:
	PYTHONPATH=src:. $(PYTHON) scripts/sync_validation_artifacts.py --root .

release-identity:
	PYTHONPATH=src:. $(PYTHON) scripts/check_release_identity.py --root . --no-git

reproducibility:
	PYTHONPATH=src:. $(PYTHON) scripts/check_reference_reproducibility.py --root .

node-reproducibility:
	PYTHONPATH=src:. $(PYTHON) scripts/check_node_reproducibility.py

burden-benchmark:
	PYTHONPATH=src:. $(PYTHON) scripts/check_burden_benchmark.py

node-bundle-check:
	@test -n "$(BUNDLE)" || (echo "BUNDLE=/path/to/node-bundle.zip is required" >&2; exit 2)
	PYTHONPATH=src:. $(PYTHON) scripts/build_node_bundle.py check $(BUNDLE)

release-attestation-verify:
	@test -n "$(ARTIFACT)" || (echo "ARTIFACT=/path/to/release-artifact is required" >&2; exit 2)
	@test -n "$(ATTESTATION_BUNDLE)" || (echo "ATTESTATION_BUNDLE=/path/to/provenance.sigstore.json is required" >&2; exit 2)
	@test -n "$(TRUSTED_ROOT)" || (echo "TRUSTED_ROOT=/path/to/trusted_root.jsonl is required" >&2; exit 2)
	@test -n "$(SOURCE_REF)" || (echo "SOURCE_REF=refs/tags/vX.Y.Z is required" >&2; exit 2)
	PYTHONPATH=src:. $(PYTHON) scripts/verify_release_attestation.py "$(ARTIFACT)" \
		--bundle "$(ATTESTATION_BUNDLE)" --trusted-root "$(TRUSTED_ROOT)" \
		--source-ref "$(SOURCE_REF)" $(if $(RECEIPT),--output "$(RECEIPT)",)

offline-node-install:
	@test -n "$(NODE_WHEEL)" || (echo "NODE_WHEEL=/path/to/rareburden.whl is required" >&2; exit 2)
	@test -n "$(WHEELHOUSE)" || (echo "WHEELHOUSE=/path/to/wheelhouse is required" >&2; exit 2)
	PYTHONPATH=src:. $(PYTHON) scripts/check_offline_node_install.py \
		--node-wheel $(NODE_WHEEL) --wheelhouse $(WHEELHOUSE) \
		--python-version $(or $(PYTHON_VERSION),3.13)

offline-node-ci: build
	rm -rf dist/wheelhouse
	mkdir -p dist/wheelhouse
	$(PYTHON) -m pip download --require-hashes --only-binary=:all: \
		--dest dist/wheelhouse --requirement requirements.txt
	PYTHONPATH=src:. $(PYTHON) scripts/check_offline_node_install.py \
		--node-wheel $(WHEEL) --wheelhouse dist/wheelhouse \
		--python-version $(or $(PYTHON_VERSION),3.13) \
		> dist/offline-install-receipt.json

clean:
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache htmlcov
	rm -f coverage.json coverage.xml junit.xml rareburden.cdx.json SHA256SUMS

build:
	$(PYTHON) scripts/build_distributions.py --root . --output dist --source-date-epoch 1760000000

package-check:
	$(PYTHON) scripts/check_built_package.py --wheel $(WHEEL) --sdist $(SDIST) \
		--name rareburden --version $(VERSION)
	$(PYTHON) -m twine check $(WHEEL) $(SDIST)

installed-package-check:
	$(PYTHON) scripts/check_installed_package.py --wheel $(WHEEL)

sbom:
	$(PYTHON) scripts/build_sbom.py --lock uv.lock --output rareburden.cdx.json \
		--name rareburden --version $(VERSION)

check: validate schemas workflows lock requirements runtime-assets-check external-receipt-check qualifying-receipts-check downstream-preparation-check single-owner-agent-governance-check track-008-freeze-readiness-check track-009-freeze-readiness-check track-009-source-profile-role-check track-010-alpha-freeze-readiness-check track-010-candidate-containment-check track-016-production-release-readiness-check package-size-check release-identity node-reproducibility burden-benchmark \
	lint format-check typecheck links safety compile test

ci: check coverage critical-coverage reproducibility

release-check: ci build package-check installed-package-check sbom

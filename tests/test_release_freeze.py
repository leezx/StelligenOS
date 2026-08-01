import unittest

from src.capabilities.release_freeze import (
    ArchitectureFreezeRequest,
    ArchitectureFreezeResult,
    ReleaseStatus,
)


class ReleaseFreezeContractTests(unittest.TestCase):
    def test_release_freeze_preserves_frozen_gate_topology(self):
        request = ArchitectureFreezeRequest(
            request_id="external:run/release-request-1",
            module_id="gen_indication_endpoint_target",
            release_version="1.0.0",
            gate_registry_version="external:registry/gates-v1",
            gate_ids_digest_ref="external:digest/gates-45",
            tpc_profile_refs=("external:profiles/tpc-v1",),
            dependency_graph_ref="external:graph/t0-t12-v1",
            phase_manifest_refs=("external:manifest/phases-0-9",),
            archived_prompt_refs=("external:prompt/archive-v1",),
            gate_extension_proposal_refs=(),
            unresolved_issue_refs=(),
        )
        self.assertEqual(request.gate_count, 45)
        with self.assertRaises(ValueError):
            ArchitectureFreezeRequest(
                request_id="external:run/release-request-1",
                module_id="gen_indication_endpoint_target",
                release_version="1.0.0",
                gate_registry_version="external:registry/gates-v1",
                gate_ids_digest_ref="external:digest/gates-45",
                tpc_profile_refs=("external:profiles/tpc-v1",),
                dependency_graph_ref="external:graph/t0-t12-v1",
                phase_manifest_refs=("external:manifest/phases-0-9",),
                archived_prompt_refs=("external:prompt/archive-v1",),
                gate_extension_proposal_refs=("external:extension/proposed-1",),
                unresolved_issue_refs=(),
            )

    def test_freeze_result_is_external_release_metadata(self):
        result = ArchitectureFreezeResult(
            request_id="external:run/release-request-1",
            status=ReleaseStatus.READY,
            release_manifest_ref="external:release/gen-iet-v1.0.0",
            immutable_contract_refs=("external:contract/frozen-v1",),
            future_extension_scope_ref="external:governance/extension-scope",
            run_ref="external:run/release-1",
        )
        self.assertEqual(result.status, ReleaseStatus.READY)


if __name__ == "__main__":
    unittest.main()

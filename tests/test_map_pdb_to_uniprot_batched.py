# tests/test_map_pdb_to_uniprot_batched.py

import pytest
from unittest.mock import patch
from protpen import enrich_utils

@patch("protpen.enrich_utils.submit_id_mapping")
@patch("protpen.enrich_utils.poll_job")
@patch("protpen.enrich_utils.get_mapping_results")
def test_map_pdb_to_uniprot_batched_mocked(get_results_mock, poll_job_mock, submit_mock):
    # Track submitted batches so we can simulate correct job IDs and results
    submitted_batches = {}

    def mock_submit(batch):
        job_id = f"mock_job_{'_'.join(batch)}"
        submitted_batches[job_id] = batch
        return job_id

    def mock_results(job_id):
        pdb_ids = submitted_batches.get(job_id, [])
        return [{"from": pdb_id, "to": f"UniProt_{pdb_id}_A"} for pdb_id in pdb_ids]

    submit_mock.side_effect = mock_submit
    poll_job_mock.return_value = True
    get_results_mock.side_effect = mock_results

    pdb_ids = ["1ABC", "2DEF", "3GHI"]
    result = enrich_utils.map_pdb_to_uniprot_batched(pdb_ids, batch_size=2)

    assert isinstance(result, dict)
    assert set(result.keys()) == set(pdb_ids)
    for pdb_id in pdb_ids:
        assert result[pdb_id] == [f"UniProt_{pdb_id}_A"]


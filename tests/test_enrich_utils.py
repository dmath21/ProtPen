# tests/test_enrich_utils.py
import os
import json
import tempfile
from unittest.mock import patch
from protpen import enrich_utils
from unittest import mock
import csv

def test_get_uniprot_info_reads_cached_json(tmp_path):
    # Create mock UniProt JSON
    uniprot_id = "P12345"
    json_dir = tmp_path / "uniprot_json_enrich"
    json_dir.mkdir()
    data = {
        "proteinDescription": {
            "recommendedName": {"fullName": {"value": "Mock Protein"}}
        },
        "uniProtKBCrossReferences": [
            {
                "database": "INTERPRO",
                "id": "IPR000001",
                "properties": [{"key": "EntryName", "value": "IPR_MOCK"}]
            },
            {
                "database": "SUPFAM",
                "id": "SF000001",
                "properties": [{"key": "EntryName", "value": "SF_MOCK"}]
            }
        ]
    }
    with open(json_dir / f"{uniprot_id}.json", "w") as f:
        json.dump(data, f)

    with patch("protpen.enrich_utils.download_uniprot_json") as mock_download:
        result = enrich_utils.get_uniprot_info(uniprot_id, str(json_dir))
        assert result["description"] == "Mock Protein"
        assert result["interpro"] == "IPR_MOCK"
        assert result["supfam"] == "SF_MOCK"
        mock_download.assert_not_called()


@patch("protpen.enrich_utils.get_mapping_results")
@patch("protpen.enrich_utils.poll_job")
@patch("protpen.enrich_utils.submit_id_mapping")
def test_id_mapping_functions(mock_submit, mock_poll, mock_results):
    mock_submit.return_value = "mock_job_id"
    mock_poll.return_value = True
    mock_results.return_value = [
        {"from": "4abc", "to": "P12345"},
        {"from": "4xyz", "to": "Q99999"}
    ]

    job_id = enrich_utils.submit_id_mapping(["4abc", "4xyz"])
    assert job_id == "mock_job_id"
    assert enrich_utils.poll_job(job_id) is True
    result = enrich_utils.get_mapping_results(job_id)
    assert result[0]["from"] == "4abc"
    assert result[0]["to"] == "P12345"

def test_extract_pdb_ids():
    input_str = "4is4-assembly1.cif.gz_H||4mdz-assembly1.cif.gz_A||5abc-assembly1.cif.gz"
    expected = ["4is4", "4mdz", "5abc"]
    assert enrich_utils.extract_pdb_ids(input_str) == expected


def test_enrich_tsv(tmp_path):
    input_path = tmp_path / "test.tsv"
    output_path = tmp_path / "enriched.tsv"

    # Write mock input
    with open(input_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "target"], delimiter="\t")
        writer.writeheader()
        writer.writerow({"query": "Q1", "target": "4is4-assembly1.cif.gz_H||4mdz-assembly1.cif.gz_A"})
        writer.writerow({"query": "Q2", "target": "5abc-assembly1.cif.gz"})

    pdb_to_info = {
        "4is4": {"description": "desc1", "interpro": "ipr1", "supfam": "sf1"},
        "4mdz": {"description": "desc2", "interpro": "ipr2", "supfam": "sf2"},
        "5abc": {"description": "desc3", "interpro": "ipr3", "supfam": "sf3"},
    }

    enrich_utils.enrich_tsv(input_path, output_path, pdb_to_info)

    with open(output_path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    assert rows[0]["UniProt_Description"] == "desc1||desc2"
    assert rows[0]["UniProt_InterPro"] == "ipr1||ipr2"
    assert rows[0]["UniProt_SUPFAM"] == "sf1||sf2"
    assert rows[1]["UniProt_Description"] == "desc3"
    assert rows[1]["UniProt_InterPro"] == "ipr3"
    assert rows[1]["UniProt_SUPFAM"] == "sf3"


@mock.patch("protpen.enrich_utils.requests.get")
def test_get_uniprot_info_mocked(mock_get, tmp_path):
    sample_response = {
        "proteinDescription": {
            "recommendedName": {
                "fullName": {"value": "Mock Protein"}
            }
        },
        "uniProtKBCrossReferences": [
            {"database": "InterPro", "id": "IPR9999"},
            {"database": "SUPFAM", "id": "SF9999"}
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = sample_response

    result = enrich_utils.get_uniprot_info("P12345", json_dir=tmp_path)
    assert result["description"] == "Mock Protein"
    assert result["interpro"] == "IPR9999"
    assert result["supfam"] == "SF9999"


@mock.patch("protpen.enrich_utils.requests.post")
def test_submit_id_mapping(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"jobId": "abc123"}
    job_id = enrich_utils.submit_id_mapping(["4is4", "4mdz"])
    assert job_id == "abc123"


@mock.patch("protpen.enrich_utils.requests.get")
def test_poll_job(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = [
        {"jobStatus": "RUNNING"},
        {"jobStatus": "FINISHED"}
    ]
    assert enrich_utils.poll_job("abc123") is True


@mock.patch("protpen.enrich_utils.requests.get")
def test_get_mapping_results(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = [
        {"results": [{"from": "4is4", "to": "P12345"}], "nextCursor": "next123"},
        {"results": [{"from": "4mdz", "to": "P67890"}]}
    ]
    results = enrich_utils.get_mapping_results("abc123")
    assert len(results) == 2
    assert results[0]["to"] == "P12345"
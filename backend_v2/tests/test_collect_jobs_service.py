import pytest
from backend_v2.application.services.collect_jobs_service import CollectJobsService, JobClientProtocol
from backend_v2.domain.repositories.job_repository import JobRepository
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
class DummyJobClient(JobClientProtocol):
    def collect_offres_paginated(self, params, page_size=150, max_offres=None):
        return []

class DummyJobRepo(JobRepository):
    def __init__(self):
        self.deactivated = []
    async def get_all_active_source_id(self):
        return []
    async def deactivate_jobs_by_source_ids(self, source_ids):
        self.deactivated.extend(source_ids)
    async def save_jobs(self, jobs):
        pass

def test_filter_existing_jobs():
    # Préparation
    jobs = [
        {"id": "1", "source_id": "1", "title": "Offre 1"},
        {"id": "2", "source_id": "2", "title": "Offre 2"},
        {"id": "3", "source_id": "3", "title": "Offre 3"},
    ]
    existing_jobs = ["2"]
    service = CollectJobsService(DummyJobClient(), DummyJobRepo())

    # Appel de la méthode privée
    filtered = service._filter_existing_jobs(jobs, existing_jobs)

    # Vérification : l'offre avec source_id "2" doit être filtrée
    assert len(filtered) == 2
    assert all(job["source_id"] != "2" for job in filtered)
    assert {job["source_id"] for job in filtered} == {"1", "3"}


def test_fetch_jobs_from_api():
    class DummyJobClient:
        def collect_offres_paginated(self, params, page_size=150, max_offres=None):
            return [
                {"id": "A", "title": "Offre A"},
                {"id": "B", "title": "Offre B"},
                {"id": "C", "title": "Offre C"},
            ]
    class DummyJobRepo:
        pass
    service = CollectJobsService(DummyJobClient(), DummyJobRepo())
    params = {"codeROME": "M1805"}
    jobs = service._fetch_jobs_from_api(params, page_size=2, max_offres=3)
    assert len(jobs) == 3
    for job, expected_id in zip(jobs, ["A", "B", "C"]):
        assert job["source_id"] == expected_id
        assert job["id"] == expected_id

import asyncio

@pytest.mark.asyncio
async def test_deactivate_missing_jobs():
    jobs = [
        {"source_id": "1"},
        {"source_id": "2"},
        {"source_id": "3"},
    ]
    existing_jobs = ["1", "2", "3", "4", "5", None]
    repo = DummyJobRepo()
    service = CollectJobsService(job_client=None, job_repo=repo)
    await service._deactivate_missing_jobs(jobs, existing_jobs)
    # Les offres "4" et "5" doivent être désactivées (None ignoré)
    assert set(repo.deactivated) == {"4", "5"}

# Pour pytest-asyncio ou pytest >= 8.1 qui supporte nativement async
def test_deactivate_missing_jobs_sync():
    asyncio.run(test_deactivate_missing_jobs())

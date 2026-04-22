from app.services.kb import KBService


def test_search_kb_returns_pricing_result() -> None:
	service = KBService()
	result = service.search_kb("pricing model", top_k=5)

	assert "results" in result
	assert len(result["results"]) > 0
	ids = [item["id"] for item in result["results"]]
	assert "KB-006" in ids

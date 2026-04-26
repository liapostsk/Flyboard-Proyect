from app.services.kb import KBService


def test_search_kb_returns_pricing_result() -> None:
	service = KBService()
	result = service.search_kb("pricing model", top_k=5)

	assert "results" in result
	assert len(result["results"]) > 0
	ids = [item["id"] for item in result["results"]]
	assert "KB-006" in ids


def test_search_kb_with_empty_tags_filter_still_returns_pricing_result() -> None:
	service = KBService()
	result = service.search_kb(
		"pricing model",
		top_k=5,
		filters={"tags": [], "audience": "customer"},
	)

	assert len(result["results"]) > 0
	ids = [item["id"] for item in result["results"]]
	assert "KB-006" in ids


def test_search_kb_crm_writeback_with_fuzzy_tags_still_returns_result() -> None:
	service = KBService()
	result = service.search_kb(
		"CRM writeback",
		top_k=5,
		filters={"tags": ["CRM", "integration"], "audience": "customer"},
	)

	assert len(result["results"]) > 0
	ids = [item["id"] for item in result["results"]]
	assert "KB-004" in ids
	kb004 = next(item for item in result["results"] if item["id"] == "KB-004")
	assert "2–5 business days" in kb004["snippet"]

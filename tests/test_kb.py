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

def test_clean_filters_normalizes_tags_and_discards_unknown_values() -> None:
	service = KBService()

	filters = service.clean_filters({"audience": "internal", "tags": ["CRM", "unknown", 123]})

	assert filters == {"audience": "internal", "tags": ["crm"]}


def test_tokenize_expands_bigrams_and_singularizes_terms() -> None:
	service = KBService()

	tokens = service._tokenize("Write backs tickets")

	assert "writeback" in tokens
	assert "ticket" in tokens


def test_build_snippet_keeps_relevant_neighbor_sentences() -> None:
	service = KBService()
	content = (
		"Intro sentence about the integration. "
		"Second sentence covers expired tokens and field mapping drift for the integration. "
		"Third sentence explains customer_id, error logs, and sample payload collection in detail. "
		"Fourth sentence adds more operational guidance and escalation notes. "
		"Fifth sentence closes with unrelated background and repeated filler to push the content well beyond the snippet threshold."
	)
	query_tokens = {"expired", "tokens", "customer", "payload"}

	snippet = service._build_snippet(content, query_tokens)

	assert "Second sentence" in snippet
	assert "Third sentence" in snippet
	assert "Fourth sentence" in snippet

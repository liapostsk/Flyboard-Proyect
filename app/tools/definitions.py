def get_tool_definitions() -> list:
    """
    Devuelve las definiciones de tools en formato JSON schema.
    Esto se pasa a OpenAI en el parámetro 'tools'.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "search_kb",
                "description": "Search the knowledge base for relevant information. Use this when the user asks a general question about Flyboard.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'pricing', 'integrations', 'onboarding')"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default 5, max 10)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 5
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filters",
                            "properties": {
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by tags"
                                },
                                "audience": {
                                    "type": "string",
                                    "enum": ["customer", "internal"],
                                    "description": "Filter by audience type"
                                }
                            }
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_ticket",
                "description": "Create a support ticket for issues that need operational attention.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Ticket title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Detailed description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Priority level"
                        }
                    },
                    "required": ["title", "body", "priority"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "schedule_followup",
                "description": "Schedule a follow-up call or message.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "datetime_iso": {
                            "type": "string",
                            "description": "ISO 8601 datetime (e.g., '2025-12-15T10:30:00Z')"
                        },
                        "contact": {
                            "type": "string",
                            "description": "Email, phone, or name"
                        },
                        "channel": {
                            "type": "string",
                            "enum": ["email", "phone", "whatsapp"],
                            "description": "Communication channel"
                        }
                    },
                    "required": ["datetime_iso", "contact", "channel"]
                }
            }
        }
    ]
from atguigu.knowledge.provider import KnowledgeProvider


class KnowledgeProviderRegistry:
    def __init__(self, providers: list[KnowledgeProvider]) -> None:

        self._providers_by_id = {p.provider_id: p for p in providers}

    def get(self, provider_id: str) -> KnowledgeProvider:
        return self._providers_by_id[provider_id]

from defrag.modules.helpers import Query, QueryResponse
from defrag.modules.docs import *

from fastapi import APIRouter

from defrag.modules.helpers.cache_manager import Memo_Redis
router = APIRouter()


__ENDPOINT_NAME__ = "docs"


@router.get(f"/{__ENDPOINT_NAME__}/single/")
@Memo_Redis.install_decorator(f"/{__ENDPOINT_NAME__}/single/")
async def search_single_source_docs(source: str, keywords: str) -> QueryResponse:
    if not ready_to_index([source]):
        if source == "tumbleweed":
            set_global_index("tumbleweed", make_tumbleweed_index(await get_data(source)))
        else:
            set_global_index("leap", make_leap_index(await get_data(source)))
    results = sorted_on_score(search_index(
        indexes[source]["index"], source, keywords))
    return QueryResponse(query=Query(service="search_docs"), results_count=len(results), results=results)


@router.get(f"/{__ENDPOINT_NAME__}/merged/")
@Memo_Redis.install_decorator(f"/{__ENDPOINT_NAME__}/merged/")
async def handle_search_docs(keywords: str) -> QueryResponse:
    if not ready_to_index(["leap", "tumbleweed"]):
        results = await make_search_set_indexes_in_parallel(keywords)
        return QueryResponse(query=Query(service="search_docs"), results_count=len(results), results=results)
    else:
        results = sorted_on_score(search_indexes_in_parallel(keywords))
        return QueryResponse(query=Query(service="search_docs"), results_count=len(results), results=results)

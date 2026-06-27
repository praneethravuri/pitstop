"""query_wikidata tool — generic SPARQL interface for F1 data from Wikidata."""

import logging

from fastmcp.exceptions import ToolError

from pitstop.clients import wikidata_client
from pitstop.exceptions import DataSourceError
from pitstop.tools.wikidata.models import WikidataResponse
from pitstop.utils import paginate, to_tool_error

logger = logging.getLogger("pitstop.wikidata")

_MAX_ROWS = 1000
_ALLOWED_PREFIXES = ("select", "ask")


def query_wikidata(
    sparql: str,
    page: int = 1,
    page_size: int = 50,
) -> WikidataResponse:
    """
    Execute a SPARQL query against the Wikidata Query Service.
    Returns flattened rows where each row is a dict of variable→value.

    Use this for F1 biographical data, career records, historical facts, and
    cross-references not covered by Jolpica or OpenF1.

    Coverage: all eras (Wikidata is a general knowledge graph).

    IMPORTANT: Only SELECT and ASK queries are accepted (read-only).
    Always include LIMIT in your query to control result size.

    Example query to find all F1 World Champions:
        SELECT ?driver ?driverLabel ?champion WHERE {
          ?driver wdt:P31 wd:Q5 .
          ?driver wdt:P166 wd:Q10454720 .
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
        } LIMIT 30
    """
    query_stripped = sparql.strip().lower()
    if not any(query_stripped.startswith(prefix) for prefix in _ALLOWED_PREFIXES):
        raise ToolError(
            "Only SELECT and ASK SPARQL queries are allowed. "
            "INSERT, DELETE, UPDATE, and other write operations are not permitted."
        )

    try:
        rows = wikidata_client.run_sparql(sparql)
    except ToolError:
        raise
    except DataSourceError as exc:
        raise to_tool_error("query_wikidata", "wikidata", exc)
    except Exception as exc:
        raise to_tool_error("query_wikidata", "wikidata", exc)

    rows = rows[:_MAX_ROWS]

    paged_rows, meta = paginate(rows, page, page_size)

    return WikidataResponse(
        query=sparql,
        rows=paged_rows,
        row_count=len(rows),
        pagination=meta if rows else None,
    )

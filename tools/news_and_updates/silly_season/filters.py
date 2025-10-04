from models import SillySeasonArticle

# Keyword sets for different silly season categories
TRANSFER_KEYWORDS = [
    "transfer", "move", "join", "joining", "signing", "signs", "switched", "switches",
    "rumor", "rumour", "linked", "target", "interest", "approach", "speculation",
    "deal", "negotiation", "contract negotiation"
]

MANAGEMENT_KEYWORDS = [
    "team principal", "technical director", "sporting director", "ceo",
    "resign", "resignation", "appointed", "appointment", "hire", "hiring",
    "depart", "departure", "replacement", "promoted", "promotion",
    "restructure", "management change"
]

CONTRACT_KEYWORDS = [
    "contract", "extension", "renewal", "renew", "extends", "extended",
    "expire", "expiring", "sign", "signed", "commit", "committed",
    "multi-year", "option", "clause"
]

TEAM_KEYWORDS = [
    "new team", "entry", "join grid", "franchise", "expansion",
    "sponsor", "sponsorship", "partnership", "technical partner",
    "supplier", "engine supplier", "power unit", "switch"
]


def filter_news_by_keywords(
    articles: list,
    keywords: list[str],
    category: str,
    query_value: str | None = None
) -> list[SillySeasonArticle]:
    """
    Filter news articles by keywords and calculate relevance score.

    Args:
        articles: List of NewsArticle objects
        keywords: List of keywords to search for
        category: Category name for the articles
        query_value: Optional filter value (driver name, team name, year)

    Returns:
        List of filtered SillySeasonArticle objects with relevance scores
    """
    filtered = []

    for article in articles:
        # Combine title and summary for searching
        content = f"{article.title} {article.summary}".lower()

        # Check if any keywords match
        matching_keywords = [kw for kw in keywords if kw.lower() in content]

        # If query_value is provided, check if it's in the content
        if query_value:
            query_match = query_value.lower() in content
            if not query_match:
                continue

        if matching_keywords:
            # Calculate relevance score based on keyword matches
            relevance_score = min(len(matching_keywords) / 3.0, 1.0)

            filtered.append(
                SillySeasonArticle(
                    title=article.title,
                    link=article.link,
                    published=article.published,
                    summary=article.summary,
                    source=article.source,
                    author=article.author,
                    category=category,
                    relevance_score=relevance_score
                )
            )

    # Sort by relevance score (highest first)
    filtered.sort(key=lambda x: x.relevance_score or 0, reverse=True)
    return filtered

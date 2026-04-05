"""Reddit post fetching — supports multiple subreddits and sorting."""

import logging
import praw
from dataclasses import dataclass, field
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class RedditPost:
    id: str
    title: str
    body: str
    author: str
    subreddit: str
    score: int
    num_comments: int
    url: str
    created_utc: float
    top_comment: str = ""
    comments: list[dict] = field(default_factory=list)

    def to_dict(self):
        d = {k: getattr(self, k) for k in self.__dataclass_fields__}
        d["author"] = str(d["author"])
        return d


def get_reddit() -> praw.Reddit:
    if not settings.reddit_client_id:
        raise ValueError(
            "Reddit client ID not configured — set SLOP_REDDIT_CLIENT_ID in .env"
        )
    return praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )


def fetch_posts(
    subreddits: list[str] | None = None,
    sort: str = "top",
    time_filter: str = "week",
    limit: int = 10,
) -> list[dict]:
    reddit = get_reddit()
    subs = subreddits or settings.default_subreddits.split(",")

    results: list[dict] = []
    for sub_name in subs:
        try:
            sub = reddit.subreddit(sub_name.strip())
            posts = _get_sorted(sub, sort, time_filter, limit)
            for p in posts:
                top_comment_text = ""
                comments_list = []
                try:
                    p.comments.replace_more(limit=0)
                    for c in list(p.comments)[:5]:
                        if hasattr(c, "body") and c.body:
                            comments_list.append(
                                {"author": str(c.author), "body": c.body}
                            )
                            if not top_comment_text and len(c.body) > 20:
                                top_comment_text = c.body
                except Exception as e:
                    logger.warning("Failed to fetch comments for %s: %s", p.id, e)

                results.append(
                    RedditPost(
                        id=p.id,
                        title=p.title,
                        body=(p.selftext or ""),
                        author=str(p.author),
                        subreddit=sub_name.strip(),
                        score=p.score,
                        num_comments=p.num_comments,
                        url=f"https://reddit.com{p.permalink}",
                        created_utc=p.created_utc,
                        top_comment=top_comment_text,
                        comments=comments_list,
                    ).to_dict()
                )
        except Exception as e:
            logger.error("Error fetching r/%s: %s", sub_name, e)

    seen = set()
    unique = []
    for p in results:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    unique.sort(key=lambda x: x["score"], reverse=True)
    return unique


def _get_sorted(sub, sort, time_filter, limit):
    if sort == "hot":
        return sub.hot(limit=limit)
    elif sort == "new":
        return sub.new(limit=limit)
    elif sort == "top":
        return sub.top(time_filter=time_filter, limit=limit)
    elif sort == "rising":
        return sub.rising(limit=limit)
    return sub.hot(limit=limit)


def get_post_text(post: dict) -> str:
    """Extract readable text for TTS: title + body or title + top comment."""
    lines = [post["title"]]
    body = (post.get("body") or "").strip()
    tc = (post.get("top_comment") or "").strip()
    if len(body) > 10:
        lines.append(body)
    elif len(tc) > 10:
        lines.append(tc)
    return "\n".join(lines)

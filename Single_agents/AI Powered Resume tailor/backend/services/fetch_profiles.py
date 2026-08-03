import re

import httpx

GITHUB_RE = re.compile(r"github\.com/([A-Za-z0-9-]+)/?$", re.IGNORECASE)


async def summarize_urls(urls: list[str]) -> str:
    """
    Given profile URLs (GitHub, portfolio, LinkedIn, etc.), pull lightweight
    public data where possible (currently GitHub via its public REST API)
    and return a text summary the AI can use as extra context. Unsupported
    URLs are passed through as plain references.
    """
    summaries = []

    async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "resume-tailor-app"}) as client:
        for raw_url in urls:
            url = (raw_url or "").strip()
            if not url:
                continue

            match = GITHUB_RE.search(url)
            try:
                if match:
                    username = match.group(1)
                    summaries.append(await _fetch_github_summary(client, username))
                else:
                    summaries.append(
                        f"Additional link provided (reference in resume/cover letter if relevant): {url}"
                    )
            except Exception:
                summaries.append(f"Additional link provided: {url}")

    return "\n\n".join(summaries)


async def _fetch_github_summary(client: httpx.AsyncClient, username: str) -> str:
    user_res = await client.get(f"https://api.github.com/users/{username}")
    if user_res.status_code != 200:
        return f"GitHub profile: https://github.com/{username}"
    user = user_res.json()

    repos_res = await client.get(
        f"https://api.github.com/users/{username}/repos",
        params={"sort": "updated", "per_page": 6},
    )
    repos = repos_res.json() if repos_res.status_code == 200 else []
    if not isinstance(repos, list):
        repos = []

    top_repos = []
    for r in repos:
        if r.get("fork"):
            continue
        lang = f" ({r['language']})" if r.get("language") else ""
        desc = r.get("description") or "No description"
        top_repos.append(f"- {r.get('name')}{lang}: {desc}")
        if len(top_repos) >= 6:
            break

    lines = [f"GitHub Profile (@{username}):"]
    if user.get("bio"):
        lines.append(f"Bio: {user['bio']}")
    if user.get("company"):
        lines.append(f"Company: {user['company']}")
    lines.append(
        f"Public repos: {user.get('public_repos', 'N/A')}, Followers: {user.get('followers', 'N/A')}"
    )
    if top_repos:
        lines.append("Notable repositories:\n" + "\n".join(top_repos))

    return "\n".join(lines)

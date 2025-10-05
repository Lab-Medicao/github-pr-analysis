import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import datetime
import csv
import os
import time
import random
import argparse
from typing import List, Optional
from tqdm import tqdm

GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}" if TOKEN else ""}

SESSION = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
    raise_on_status=False,
)
adapter = HTTPAdapter(max_retries=retry_strategy)
SESSION.mount("https://", adapter)
SESSION.mount("http://", adapter)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "datasets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

QUERY_DIR = os.path.join(SCRIPT_DIR, "queries")
os.makedirs(QUERY_DIR, exist_ok=True)
REPO_QUERY_FILE = os.path.join(QUERY_DIR, "repo_query.graphql")
PRS_QUERY_FILE = os.path.join(QUERY_DIR, "pr_query.graphql")

def run_query(query, variables, max_retries=5):
    delay = 2
    for attempt in range(max_retries):
        try:
            response = SESSION.post(
                GITHUB_API_URL,
                json={"query": query, "variables": variables},
                headers=HEADERS,
                timeout=45,
            )
            if response.status_code != 200:
                
                msg = response.text
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type and "<title>" in msg:
                    try:
                        title = msg.split("<title>", 1)[1].split("</title>", 1)[0]
                        msg = f"{title} (HTML)"
                    except Exception:
                        msg = "HTML error page"
                raise Exception(f"HTTP {response.status_code}: {msg}")

            data = response.json()
            if "errors" in data and data["errors"]:
                
                raise Exception(f"GraphQL errors: {data['errors']}")

            if "data" not in data:
                raise Exception(f"Resposta inesperada: {data}")

            return data
        except Exception as e:
            print(f"⚠️ Erro na requisição ({e}), tentativa {attempt+1}/{max_retries}. Retentando em {delay}s...")
            time.sleep(delay + random.uniform(0, 1)) 
            delay *= 2
    raise Exception("❌ Falha após várias tentativas.")

def filter_prs(prs):
    filtered = []
    for pr in prs:
        node = pr["node"]

        if node["reviews"]["totalCount"] < 1:
            continue

        created = datetime.datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
        closed_or_merged = node["mergedAt"] or node["closedAt"]
        if not closed_or_merged:
            continue

        closed_or_merged = datetime.datetime.fromisoformat(closed_or_merged.replace("Z", "+00:00"))
        delta = closed_or_merged - created

        if delta.total_seconds() >= 3600:  
            hours = round(delta.total_seconds() / 3600, 2)
            filtered.append([
                node["number"],
                node["title"],
                node["author"]["login"] if node["author"] else "unknown",
                node["createdAt"],
                closed_or_merged.isoformat(),
                node["reviews"]["totalCount"],
                hours
            ])
    return filtered

def save_repo_csv(repo_name, data):
    filename = os.path.join(OUTPUT_DIR, f"{repo_name.replace('/', '_')}.csv")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "number",
            "title",
            "author",
            "createdAt",
            "closedOrMergedAt",
            "reviewsCount",
            "hoursOpen",
            "merged",
            "additions",
            "deletions",
            "changedFiles",
            "bodyLength",
            "issueCommentsCount",
            "reviewThreadsCount",
            "interactionsCount",
            "finalReviewState",
        ])
        writer.writerows(data)
    print(f"✅ PRs do repo {repo_name} salvos em {filename}")


def _compute_final_review_state(review_nodes: List[dict]) -> str:
    """Retorna o estado final da revisão (último review submetido)."""
    if not review_nodes:
        return "NONE"
    nodes = [n for n in review_nodes if n.get("submittedAt") or n.get("createdAt")]
    if not nodes:
        return "NONE"
    nodes.sort(key=lambda n: n.get("submittedAt") or n.get("createdAt"))  
    return nodes[-1].get("state", "NONE") or "NONE"


def collect_single_repo(owner: str, name: str, max_prs: Optional[int] = None):
    """Generator que coleta PRs de um único repositório, retornando um PR por vez."""
    after = None
    with open(os.path.join(QUERY_DIR, "pr_query.graphql"), "r") as f:
        query = f.read()

    total = 0
    while True:
        data = run_query(query, {"owner": owner, "name": name, "after": after})
        pr_container = data["data"]["repository"]["pullRequests"]
        
        if "nodes" in pr_container:
            pr_nodes = pr_container["nodes"]
        else:  
            pr_nodes = [edge["node"] for edge in pr_container.get("edges", [])]
        page_info = pr_container["pageInfo"]

        for node in pr_nodes:
            reviews_total = (node.get("reviews") or {}).get("totalCount", 0)
            if reviews_total < 1:
                continue

            created = datetime.datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
            closed_or_merged_raw = node.get("mergedAt") or node.get("closedAt")
            if not closed_or_merged_raw:
                continue
            closed_or_merged = datetime.datetime.fromisoformat(closed_or_merged_raw.replace("Z", "+00:00"))
            delta = closed_or_merged - created
            if delta.total_seconds() < 3600:
                continue

            hours = round(delta.total_seconds() / 3600, 2)
            additions = node.get("additions") or 0
            deletions = node.get("deletions") or 0
            changed_files = node.get("changedFiles") or 0
            body_len = len(node.get("bodyText") or "")
            issue_comments = (node.get("comments") or {}).get("totalCount", 0)
            review_threads = (node.get("reviewThreads") or {}).get("totalCount", 0)
            interactions = issue_comments + review_threads
            
            review_nodes = ((node.get("reviews") or {}).get("nodes") or [])
            if review_nodes:
                final_state = _compute_final_review_state(review_nodes)
            else:
                
                final_state = "MERGED" if node.get("merged") else "CLOSED"

            yield [
                node["number"],
                node.get("title") or "",
                (node.get("author") or {}).get("login", "unknown"),
                node["createdAt"],
                closed_or_merged.isoformat(),
                reviews_total,
                hours,
                bool(node.get("merged")),
                additions,
                deletions,
                changed_files,
                body_len,
                issue_comments,
                review_threads,
                interactions,
                final_state,
            ]
            total += 1
            if max_prs and total >= max_prs:
                return

        if page_info["hasNextPage"]:
            after = page_info["endCursor"]
        else:
            break


def run_single_repo_mode(repo: str, max_prs: int | None):
    if "/" not in repo:
        raise SystemExit("--repo deve estar no formato owner/name, ex: facebook/react")

    owner, name = repo.split("/", 1)
    start_time = time.time()
    collected = []

    repo_data = run_query(
        """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            pullRequests {
              totalCount
            }
          }
        }
        """,
        {"owner": owner, "name": name}
    )

    total_prs = repo_data["data"]["repository"]["pullRequests"]["totalCount"]

    
    with tqdm(total= total_prs, desc=f"PRs {owner}/{name}", unit="pr") as pbar:
        for pr in collect_single_repo(owner, name, max_prs):
            collected.append(pr)
            pbar.update(1)

    save_repo_csv(f"{owner}/{name}", collected)

    elapsed = round((time.time() - start_time) / 60, 2)
    print(f"\n✅ {len(collected)} PRs coletados de {owner}/{name} em {elapsed} minutos")


def run_multi_repo_mode():
    """Executa o fluxo para varrer múltiplos repositórios populares."""
    start_time = time.time()
    repo_count = 0
    after_repo = None

    processed_repos = {f.split(".csv")[0] for f in os.listdir(OUTPUT_DIR)}

    
    with open(REPO_QUERY_FILE, "r", encoding="utf-8") as f:
        repo_query_text = f.read()
    with open(PRS_QUERY_FILE, "r", encoding="utf-8") as f:
        prs_query_text = f.read()

    with tqdm(total=200, desc="Processando repositórios", unit="repos") as pbar_repos:
        while repo_count < 200:
            repo_data = run_query(repo_query_text, {"after": after_repo})
            edges = repo_data["data"]["search"]["edges"]

            for repo in edges:
                repo_node = repo["node"]
                owner = repo_node["owner"]["login"]
                name = repo_node["name"]
                repo_name = f"{owner}/{name}"

                if repo_node["pullRequests"]["totalCount"] < 100:
                    continue

                if repo_name.replace("/", "_") in processed_repos:
                    print(f"⏭️ Pulando {repo_name}, já processado.")
                    repo_count += 1
                    pbar_repos.update(1)
                    continue

                repo_prs = collect_repo_prs(owner, name, repo_node, prs_query_text)
                save_repo_csv(repo_name, repo_prs)

                repo_count += 1
                pbar_repos.update(1)

                if repo_count >= 200:
                    break

            page_info = repo_data["data"]["search"]["pageInfo"]
            if page_info["hasNextPage"]:
                after_repo = page_info["endCursor"]
            else:
                break

    elapsed = round((time.time() - start_time) / 60, 2)
    print(f"\n✅ Tempo total de execução (multi-repo): {elapsed} minutos")


def collect_repo_prs(owner: str, name: str, repo_node: dict, prs_query_text: str) -> list:
    """Coleta PRs de um repositório com barra de progresso."""
    after_pr = None
    repo_prs = []
    pr_total = repo_node["pullRequests"]["totalCount"]

    with tqdm(total=pr_total, desc=f"PRs {owner}/{name}", unit="pr", leave=False) as pbar_prs:
        while True:
            prs_data = run_query(prs_query_text, {"owner": owner, "name": name, "after": after_pr})
            pr_container = prs_data["data"]["repository"]["pullRequests"]
            if "nodes" in pr_container:
                pr_nodes = pr_container["nodes"]
            else:
                pr_nodes = [edge["node"] for edge in pr_container.get("edges", [])]

            for node in pr_nodes:
                reviews_total = (node.get("reviews") or {}).get("totalCount", 0)
                if reviews_total < 1:
                    continue
                created = datetime.datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
                closed_or_merged_raw = node.get("mergedAt") or node.get("closedAt")
                if not closed_or_merged_raw:
                    continue
                closed_or_merged = datetime.datetime.fromisoformat(closed_or_merged_raw.replace("Z", "+00:00"))
                delta = closed_or_merged - created
                if delta.total_seconds() < 3600:
                    continue

                hours = round(delta.total_seconds() / 3600, 2)
                additions = node.get("additions") or 0
                deletions = node.get("deletions") or 0
                changed_files = node.get("changedFiles") or 0
                body_len = len(node.get("bodyText") or "")
                issue_comments = (node.get("comments") or {}).get("totalCount", 0)
                review_threads = (node.get("reviewThreads") or {}).get("totalCount", 0)
                interactions = issue_comments + review_threads
                review_nodes = ((node.get("reviews") or {}).get("nodes") or [])
                if review_nodes:
                    final_state = _compute_final_review_state(review_nodes)
                else:
                    final_state = "MERGED" if node.get("merged") else "CLOSED"

                repo_prs.append([
                    node["number"],
                    node.get("title") or "",
                    (node.get("author") or {}).get("login", "unknown"),
                    node["createdAt"],
                    closed_or_merged.isoformat(),
                    reviews_total,
                    hours,
                    bool(node.get("merged")),
                    additions,
                    deletions,
                    changed_files,
                    body_len,
                    issue_comments,
                    review_threads,
                    interactions,
                    final_state,
                ])

            page_info = pr_container["pageInfo"]
            pbar_prs.update(len(pr_nodes))

            if page_info["hasNextPage"]:
                after_pr = page_info["endCursor"]
            else:
                break

    return repo_prs


def main():
    parser = argparse.ArgumentParser(description="Coletor de PRs via GitHub GraphQL")
    parser.add_argument("--repo", help="Repositório único no formato owner/name para teste")
    parser.add_argument("--max-prs", type=int, default=None, help="Limite de PRs ao coletar um único repositório")
    args = parser.parse_args()

    if args.repo:
        run_single_repo_mode(args.repo, args.max_prs)
    else:
        run_multi_repo_mode()


if __name__ == "__main__":
    main()

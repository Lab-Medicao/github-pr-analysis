import requests
import datetime
import csv
import os
import time
import random
from pathlib import Path
from tqdm import tqdm
import argparse

# =============================
# Configuração inicial
# =============================

GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "datasets"
QUERY_DIR = BASE_DIR / "queries"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(QUERY_DIR, exist_ok=True)

# =============================
# Funções utilitárias
# =============================

def load_query(filename: str) -> str:
    """Carrega o conteúdo de um arquivo .graphql"""
    path = QUERY_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def run_query(query, variables, max_retries=5):
    """Executa query no GraphQL com retry/backoff"""
    if not TOKEN:
        raise RuntimeError("❌ GITHUB_TOKEN não definido!")

    delay = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(
                GITHUB_API_URL,
                json={"query": query, "variables": variables},
                headers=HEADERS,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if "errors" in data and (not data.get("data")):
                    msg = data["errors"][0].get("message", "Erro GraphQL desconhecido")
                    raise Exception(f"GraphQL error: {msg}")
                return data
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"⚠️ Erro na requisição ({e}), tentativa {attempt+1}/{max_retries}. Retentando em {delay}s...")
            time.sleep(delay + random.uniform(0, 1))
            delay *= 2
    raise Exception("❌ Falha após várias tentativas.")

# =============================
# Filtros de PRs por tipo
# =============================

def filter_meta(prs):
    """Extrai informações de metadados (tamanho, tempo, descrição, feedback final)."""
    data = []
    for pr in prs:
        node = pr["node"]
        created = node.get("createdAt")
        closed = node.get("mergedAt") or node.get("closedAt")

        hours_open = None
        if created and closed:
            dt_created = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
            dt_closed = datetime.datetime.fromisoformat(closed.replace("Z", "+00:00"))
            delta = dt_closed - dt_created
            hours_open = round(delta.total_seconds() / 3600, 2)

        data.append([
            node["number"],
            node.get("title", ""),
            node["author"]["login"] if node.get("author") else "unknown",
            node.get("createdAt"),
            closed,
            node.get("merged", False),
            node.get("additions", 0),
            node.get("deletions", 0),
            node.get("changedFiles", 0),
            len(node.get("bodyText", "")) if node.get("bodyText") else 0,
            hours_open,
        ])
    return data

def filter_interactions(prs):
    """Extrai informações sobre interações (comentários e revisões)."""
    data = []
    for pr in prs:
        node = pr["node"]
        data.append([
            node["number"],
            node.get("title", ""),
            node["author"]["login"] if node.get("author") else "unknown",
            node["comments"]["totalCount"],
            node["reviewThreads"]["totalCount"],
            node["reviews"]["totalCount"],
        ])
    return data

def filter_reviews(prs):
    """Extrai estados das revisões (APPROVED, CHANGES_REQUESTED, etc)."""
    data = []
    for pr in prs:
        node = pr["node"]
        for r in node.get("reviews", {}).get("nodes", []):
            data.append([
                node["number"],
                node.get("title", ""),
                node["author"]["login"] if node.get("author") else "unknown",
                r.get("state"),
                r.get("submittedAt"),
                node.get("reviewDecision"),
            ])
    return data

# =============================
# Função principal de coleta
# =============================

def collect_single_repo(owner, name, query, filter_fn, query_type, max_prs=None):
    repo_name = f"{owner}/{name}"
    repo_prs = []
    after_pr = None

    # Primeira chamada para pegar totalCount
    prs_data = run_query(query, {"owner": owner, "name": name, "after": after_pr})
    total_prs = prs_data["data"]["repository"]["pullRequests"]["totalCount"]

    with tqdm(total=total_prs, desc=f"PRs {repo_name} [{query_type}]") as pbar:
        while True:
            prs_data = run_query(query, {"owner": owner, "name": name, "after": after_pr})
            prs = prs_data["data"]["repository"]["pullRequests"]["edges"]

            repo_prs.extend(filter_fn(prs))

            page_info = prs_data["data"]["repository"]["pullRequests"]["pageInfo"]
            pbar.update(len(prs))

            if max_prs and len(repo_prs) >= max_prs:
                repo_prs = repo_prs[:max_prs]
                break

            if page_info["hasNextPage"]:
                after_pr = page_info["endCursor"]
            else:
                break

    save_repo_csv(repo_name, repo_prs, query_type)
    return repo_name, repo_prs

def collect_multiple_repos(query_type=None, max_prs=None, limit=200):
    """Coleta dados de múltiplos repositórios populares (até `limit`)."""
    REPO_QUERY = load_query("repo_query.graphql")
    repo_count = 0
    after_repo = None

    with tqdm(total=limit, desc="Processando repositórios") as pbar_repos:
        while repo_count < limit:
            repo_data = run_query(REPO_QUERY, {"after": after_repo})
            edges = repo_data["data"]["search"]["edges"]

            for repo in edges:
                repo_node = repo["node"]
                owner = repo_node["owner"]["login"]
                name = repo_node["name"]
                repo_name = f"{owner}/{name}"

                if repo_node["pullRequests"]["totalCount"] < 100:
                    continue  # pula repositórios com poucos PRs

                print(f"\n🔹 Coletando {repo_name}...")

                if query_type:
                    # coleta só um tipo
                    query, filter_fn = queries[query_type]
                    collect_single_repo(owner, name, query, filter_fn, query_type, max_prs)
                else:
                    # coleta todos os tipos
                    for qtype, (query, filter_fn) in queries.items():
                        collect_single_repo(owner, name, query, filter_fn, qtype, max_prs)

                repo_count += 1
                pbar_repos.update(1)
                if repo_count >= limit:
                    break

            page_info = repo_data["data"]["search"]["pageInfo"]
            if page_info["hasNextPage"]:
                after_repo = page_info["endCursor"]
            else:
                break


def save_repo_csv(repo_name, data, query_type):
    repo_dir = OUTPUT_DIR / repo_name.replace("/", "_")
    repo_dir.mkdir(parents=True, exist_ok=True)
    filename = repo_dir / f"pr_{query_type}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if query_type == "meta":
            writer.writerow([
                "number","title","author","createdAt","closedAt_or_mergedAt",
                "merged","additions","deletions","changedFiles",
                "descriptionSize", "hoursOpen"
            ])
        elif query_type == "interactions":
            writer.writerow(["number", "title", "author", "commentsCount","reviewThreadsCount","reviewsCount"])
        elif query_type == "reviews":
            writer.writerow(["number", "title", "author", "reviewState", "submittedAt", "reviewDecision"])
        writer.writerows(data)

    print(f"✅ PRs {query_type} do repo {repo_name} salvos em {filename}")

# =============================
# Main
# =============================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="Repositório único no formato owner/name")
    parser.add_argument("--max-prs", type=int, default=None, help="Limite de PRs para teste")
    parser.add_argument("--query-type", choices=["meta", "interactions", "reviews"], required=False,
                        help="Tipo de coleta. Se não informado, roda todos em sequência")
    parser.add_argument("--limit", type=int, default=200, help="Número de repositórios para coletar no modo múltiplo")
    args = parser.parse_args()

    queries = {
        "meta": (load_query("pr_metadata_query.graphql"), filter_meta),
        "interactions": (load_query("pr_interactions_query.graphql"), filter_interactions),
        "reviews": (load_query("pr_review_state_query.graphql"), filter_reviews),
    }

    start_time = time.time()

    if args.repo:
        # Modo repo único
        if "/" not in args.repo:
            raise SystemExit("--repo deve estar no formato owner/name, ex: facebook/react")

        owner, name = args.repo.split("/", 1)

        if args.query_type:
            query, filter_fn = queries[args.query_type]
            collect_single_repo(owner, name, query, filter_fn, args.query_type, args.max_prs)
        else:
            for qtype, (query, filter_fn) in queries.items():
                collect_single_repo(owner, name, query, filter_fn, qtype, args.max_prs)
    else:
        # Modo múltiplos repositórios
        collect_multiple_repos(args.query_type, args.max_prs, args.limit)

    elapsed = round((time.time() - start_time) / 60, 2)
    print(f"\n⏱️ Tempo total de execução: {elapsed} minutos")

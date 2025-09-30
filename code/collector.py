import requests
import datetime
import csv
import os
import time
import random
from tqdm import tqdm

GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

OUTPUT_DIR = "datasets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

QUERY_DIR = "queries"
os.makedirs(QUERY_DIR, exist_ok=True)

REPO_QUERY = QUERY_DIR + "/repo_query.graphql"
PRS_QUERY = QUERY_DIR + "/pr_query.graphql"

def run_query(query, variables, max_retries=5):
    delay = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(
                GITHUB_API_URL, json={"query": query, "variables": variables}, headers=HEADERS, timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erro {response.status_code}: {response.text}")
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

        if delta.total_seconds() >= 3600:  # >= 1h
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
        writer.writerow(["number", "title", "author", "createdAt", "closedOrMergedAt", "reviewsCount", "hoursOpen"])
        writer.writerows(data)
    print(f"✅ PRs do repo {repo_name} salvos em {filename}")

if __name__ == "__main__":
    start_time = time.time()
    repo_count = 0
    after_repo = None

    processed_repos = {f.split(".csv")[0] for f in os.listdir(OUTPUT_DIR)}

    with tqdm(total=200, desc="Processando repositórios") as pbar_repos:
        while repo_count < 200:
            repo_data = run_query(REPO_QUERY, {"after": after_repo})
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
                after_pr = None
                repo_prs = []

                pr_total = repo_node["pullRequests"]["totalCount"]
                with tqdm(total=pr_total, desc=f"PRs {repo_name}", leave=False) as pbar_prs:
                    while True:
                        prs_data = run_query(PRS_QUERY, {"owner": owner, "name": name, "after": after_pr})
                        prs = prs_data["data"]["repository"]["pullRequests"]["edges"]

                        repo_prs.extend(filter_prs(prs))

                        page_info = prs_data["data"]["repository"]["pullRequests"]["pageInfo"]
                        pbar_prs.update(len(prs))

                        if page_info["hasNextPage"]:
                            after_pr = page_info["endCursor"]
                        else:
                            break

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
    print(f"\nTempo total de execução: {elapsed} minutos")

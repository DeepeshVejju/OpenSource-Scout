import typer
from rich import print

from packages.agents.coordinator import Coordinator

app = typer.Typer(no_args_is_help=True)


@app.command()
def search(
    q: str = typer.Option(..., "--q", help="GitHub search query"),
    top: int = typer.Option(10, "--top", min=1, max=50, help="Number of repos to return"),
) -> None:
    coord = Coordinator()
    result = coord.run(query=q, top_n=top, analyze_n=0)

    for i, c in enumerate(result["top"], start=1):
        repo = c["repo"]
        score = c["score"]
        reasons = ", ".join(c["reasons"][:3])
        print(f"{i}. [bold]{repo['full_name']}[/bold] ({score}) - {repo['url']}")
        if reasons:
            print(f"   {reasons}")


@app.command()
def run(
    q: str = typer.Option(..., "--q", help="GitHub search query"),
    top: int = typer.Option(10, "--top", min=1, max=50, help="Number of repos to consider"),
    analyze: int = typer.Option(3, "--analyze", min=0, max=10, help="Number of top repos to analyze"),
) -> None:
    coord = Coordinator()
    result = coord.run(query=q, top_n=top, analyze_n=analyze)

    print(f"[bold]Query:[/bold] {result['query']}\n")

    print("[bold]Top Repos:[/bold]")
    for i, c in enumerate(result["top"], start=1):
        repo = c["repo"]
        print(f"{i}. {repo['full_name']} ({c['score']}) - {repo['url']}")

    if analyze == 0:
        return

    print("\n[bold]Analysis:[/bold]")
    for block in result["analyzed"]:
        repo = block["repo"]["repo"]
        print(f"\n[bold]{repo['full_name']}[/bold] - {repo['url']}")

        analysis = block["analysis"]
        if analysis.get("summary"):
            print(f"  [bold]Summary:[/bold] {analysis['summary']}")
        if analysis.get("how_to_run"):
            print("  [bold]How to run:[/bold]")
            print(f"{analysis['how_to_run'][:800]}")

        stack = block["stack"]
        if stack.get("languages"):
            langs = ", ".join([f"{k}" for k in stack["languages"].keys()])
            print(f"  [bold]Languages:[/bold] {langs}")
        if stack.get("frameworks"):
            print(f"  [bold]Frameworks:[/bold] {', '.join(stack['frameworks'])}")
        if stack.get("tools"):
            print(f"  [bold]Tools:[/bold] {', '.join(stack['tools'])}")
        if stack.get("infra_signals"):
            print(f"  [bold]Infra:[/bold] {', '.join(stack['infra_signals'])}")

        contrib = block["contrib"]
        issues = contrib.get("issues", [])
        print("  [bold]Contribution issues:[/bold]")
        if not issues:
            print("    None found (try browsing open issues manually).")
        else:
            for it in issues[:5]:
                print(f"    - {it['title']} ({it['url']})")

        improve = block["improve"]
        quick_wins = improve.get("quick_wins", [])
        evidence = improve.get("evidence", [])

        if quick_wins:
            print("  [bold]Quick wins:[/bold]")
            for s in quick_wins[:5]:
                print(f"    - {s}")

        if evidence:
            print("  [bold]Evidence:[/bold]")
            for e in evidence[:8]:
                print(f"    - {e}")


if __name__ == "__main__":
    app()

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def search(
    q: str = typer.Option(..., "--q", help="GitHub search query"),
    top: int = typer.Option(10, "--top", min=1, max=50, help="Number of repos to return"),
) -> None:
    """
    Search GitHub repositories and print basic results (placeholder).
    """
    typer.echo(f"[TODO] search: q={q!r}, top={top}")


@app.command()
def run(
    q: str = typer.Option(..., "--q", help="GitHub search query"),
    top: int = typer.Option(10, "--top", min=1, max=50, help="Number of repos to consider"),
    analyze: int = typer.Option(3, "--analyze", min=1, max=10, help="Number of top repos to analyze"),
) -> None:
    """
    Run the multi-agent pipeline (placeholder).
    """
    typer.echo(f"[TODO] run: q={q!r}, top={top}, analyze={analyze}")


if __name__ == "__main__":
    app()

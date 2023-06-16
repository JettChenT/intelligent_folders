import typer
from global_config import GlobalConfig
from pathlib import Path
from register.cron import gen_crontab

app = typer.Typer()

@app.command()
def register_cron():
    """Register the service to run on reboot."""
    res = gen_crontab()
    typer.echo(f"Registered cron job: {res}")

@app.command()
def add_dir(path:str):
    """Add a directory to watch."""
    global_config = GlobalConfig()
    global_config.add_watch_dir(Path(path))
    typer.echo(f"Added directory {path}")

@app.command()
def list_dirs():
    """List all directories being watched."""
    global_config = GlobalConfig()
    for d in global_config.watch_dirs:
        typer.echo(str(d))

if __name__ == "__main__":
    app()
import typer
from global_config import GlobalConfig
from pathlib import Path
from register.cron import gen_crontab
import requests
import service
import subprocess
import sys

app = typer.Typer()

def is_server_running():
    try:
        requests.get("http://localhost:1319/status")
        return True
    except requests.exceptions.ConnectionError:
        return False

@app.command()
def register_cron():
    """Register the service to run on reboot."""
    res = gen_crontab()
    if res:
        typer.echo("Cron job already exists") 
    else:
        typer.echo(f"Registered cron job: {res}")

@app.command()
def add_dir(path:str):
    """Add a directory to watch."""
    pth = Path(path).resolve()
    try:
        res = requests.post("http://localhost:1319/add-directory", json={"dir": str(pth)})
        if res.status_code == 200:
            typer.echo("Added directory")
        else:
            typer.echo(f"Error adding directory: {res}")
    except requests.exceptions.ConnectionError:
        typer.echo("Service is not running")

@app.command()
def rm_dir(path:str):
    pth = Path(path).resolve()
    try:
        res = requests.post("http://localhost:1319/remove-directory", json={"dir": str(pth)})
        if res.status_code == 200:
            typer.echo("Removed directory")
        else:
            typer.echo(f"Error removing directory: {res}")
    except requests.exceptions.ConnectionError:
        typer.echo("Service is not running")


@app.command()
def list_dirs():
    """List all directories being watched."""
    try:
        res = requests.get("http://localhost:1319/list-directories")
        if res.status_code == 200:
            typer.echo(res.json()['directories'])
        else:
            typer.echo(f"Error getting directories: {res}")
    except requests.exceptions.ConnectionError:
        typer.echo("Service is not running")


@app.command()
def status():
    """Get the status of the service."""
    try:
        requests.get("http://localhost:1319/status")
        typer.echo("Service is running")
    except requests.exceptions.ConnectionError:
        typer.echo("Service is not running")

@app.command()
def start():
    from register.cron import get_command
    try:
        requests.get("http://localhost:1319/status")
        typer.echo("Service is already running")
    except requests.exceptions.ConnectionError:
        subprocess.Popen(get_command().split(), stdout=subprocess.DEVNULL)
        print("Started service")
        sys.exit(0)

@app.command()
def stop():
    if not is_server_running():
        typer.echo("Service is not running")
        return
    try:
        requests.post("http://localhost:1319/stop")
        typer.echo("Service stopped unsuccessfully!")
    except requests.exceptions.ConnectionError:
        typer.echo("Stoped service.")

@app.command()
def restart():
    stop()
    start()
    
@app.command()
def print_loc():
    typer.echo(str(GlobalConfig().get_app_path()))

if __name__ == "__main__":
    app()
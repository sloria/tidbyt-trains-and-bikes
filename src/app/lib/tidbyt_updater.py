import subprocess
import sys

import click
from environs import Env

from .tidbyt import push_to_tidbyt, render_applet

env = Env(eager=False)
env.read_env()
API_KEY = env.str("TIDBYT_API_KEY")
DEVICE_ID = env.str("TIDBYT_DEVICE_ID")
INSTALLATION_ID = env.str("TIDBYT_INSTALLATION_ID", default="rctransport")
env.seal()


@click.group()
def cli():
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--as-bytes", is_flag=True, help="Return the rendered image as raw bytes."
)
def render(*, path: str, as_bytes: bool):
    """Render a Pixlet starlark app to a webp image."""
    click.echo(f"Rendering {path} and writing to stdout...", file=sys.stderr)
    image_data = render_applet(path, as_bytes=as_bytes)
    if as_bytes:
        sys.stdout.buffer.write(image_data)
    else:
        sys.stdout.write(image_data)
    click.secho("Finished.", fg="green", file=sys.stderr)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def push(path: str):
    """Render and push a Pixlet starlark app to a Tidbyt device."""
    click.secho(f"Rendering {path} to a webp file", file=sys.stderr)
    image_data = render_applet(path)
    push_to_tidbyt(
        image_data=image_data,
        api_key=API_KEY,
        device_id=DEVICE_ID,
        installation_id=INSTALLATION_ID,
    )
    click.secho(f"Successfully pushed {path} to Tidbyt.", fg="green", file=sys.stderr)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def serve(path: str):
    """Serve a Pixlet starlark app. For development purposes only."""
    subprocess.run(
        [  # noqa: S607
            "pixlet",
            "serve",
            path,
        ],
        check=False,
    )


if __name__ == "__main__":
    cli()

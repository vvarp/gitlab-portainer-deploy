import json
import os
import sys

import click
import requests


@click.command()
@click.option("--portainer-url", envvar="PORTAINER_URL", required=True, help="Portainer instance URL")
@click.option("--portainer-username", envvar="PORTAINER_USERNAME", required=True, help="Portainer username")
@click.option("--portainer-password", envvar="PORTAINER_PASSWORD", required=True, help="Portainer password")
@click.option("--portainer-stack", envvar="PORTAINER_STACK", default=None, required=True)
@click.option("--stackfile", envvar="STACKFILE", default="docker-stack.yml", required=True)
@click.option("--env-var", "-e", multiple=True, default=[], required=False)
def main(portainer_url, portainer_username, portainer_password, portainer_stack, stackfile, env_var):
    # Build list of env vars to be passed on to Portainer
    stack_env = []
    if len(env_var) > 0:
        click.echo("Environment variables for stackfile:\n")
        for e in env_var:
            name = e.split("=")[0]
            value = "=".join(e.split("=")[1:])
            stack_env.append({
                "name": name,
                "value": value,
            })
            click.echo(f"  {name}: {value}")
    else:
        click.echo("No environment variables for stackfile.")

    # Get auth token
    click.echo(click.style("\nGetting auth token...", fg="yellow"), nl=False)
    auth = requests.post(f"{portainer_url}/auth", json={
        "Username": portainer_username,
        "Password": portainer_password,
    })

    if auth.status_code != 200:
        click.echo(click.style(f"\nHTTP {auth.status_code} error while trying to obtain JWT token", fg="red"))
        sys.exit(1)

    headers = {"Authorization": "Bearer " + auth.json()["jwt"]}
    click.echo(click.style(" done", fg="green"))

    # Try to read stackfile contents
    click.echo(click.style("Checking for stackfile...", fg="yellow"), nl=False)
    if os.path.isfile(stackfile):
        with open(stackfile) as f:
            stackfilecontent = f.read()
    else:
        click.echo(click.style(" can't find stackfile", fg="red"))
        sys.exit(1)

    click.echo(click.style(" done", fg="green"))

    # Get IDs for target endpoint and stack
    click.echo(click.style("Getting target stack ID...", fg="yellow"), nl=False)
    stacks = requests.get(f"{portainer_url}/stacks", headers=headers)
    if stacks.status_code != 200:
        click.echo(f"\nHTTP {auth.status_code} error while trying to get list of Portainer stacks")
        sys.exit(1)

    stack_id = None
    for s in stacks.json():
        if s["Name"] == portainer_stack:
            stack_id = str(s["Id"])
            endpoint_id = str(s["EndpointId"])

    if stack_id is None:
        click.echo(click.style(f" can't find stack \"{portainer_stack}\" in Portainer", fg="red"))
        sys.exit(1)

    click.echo(click.style(" done", fg="green"))

    # Update stack
    click.echo(click.style("Requesting stack update...", fg="yellow"), nl=False)
    r = requests.put(
        f"{portainer_url}/stacks/{stack_id}?endpointId={endpoint_id}",
        headers=headers,
        json={
            "StackFileContent": stackfilecontent,
            "Env": stack_env,
            "Prune": False
        }
    )
    click.echo(click.style(" done", fg="green"))

    click.echo(f"\nRequest to update stack finished with HTTP {r.status_code}: \n{json.dumps(r.json(), indent=4)}\n")

    if r.status_code != 200:
        click.echo(click.style(f"Deployment failed", fg="red"))
        sys.exit(1)

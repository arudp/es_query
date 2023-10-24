"""
Command to run an ElasticSearch query from the command line.

Deps to install with pip3:
pip3 install --upgrade pip && pip3 install click requests

Pipe the query through the stdin (e.g., cat file or echo) and run it:
```
echo ${QUERY} | python3 es.py --host es-prod --endpoint project_drafts/_search --pretty
```

> Where `es-prod` is the name of the host in `/etc/hosts`

Of course, this can be written to a file or piped into something like jq for pretty printing.
I'd recommend to alias it in your `.rc` file:
```
alias es_prod="python3 /path/to/es.py --host es-prod --endpoint

$ echo ${QUERY} | es_prod project_drafts/_search --pretty | jq | less
```
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Dict

import requests
from click import STRING, command, get_text_stream, option


def print_err(*args, **kwargs) -> None:
    """Print stuff in a way that doesn't get captured by pipes."""

    print(*args, file=sys.stderr, **kwargs)


ES_DEFAULT_PORT: int = 9200
ES_URL: str = "http://{host}:{port}"


@dataclass
class ElasticSearchCommand:
    host: str
    port: str
    endpoint: str
    query: dict = field(default_factory=dict)
    pretty: bool = False

    def run(self) -> None:
        self.query = self._get_query_from_stdin()
        self.port = self.port or ES_DEFAULT_PORT

        url: str = self._get_url()

        print_err(f"{url} {self.query}")

        response: requests.Response = self._request(url)

        indent_args = {}
        if self.pretty:
            indent_args = {"indent": 2}

        print(json.dumps(json.loads(response.text), **indent_args))

    def _get_query_from_stdin(self) -> dict:
        query_raw = "".join(get_text_stream("stdin").readlines())
        return json.loads(query_raw)

    def _get_url(self) -> str:
        if not self.host:
            raise Exception(f"No host was given [{self.host}] not supported")

        base_url = ES_URL.format(host=self.host, port=self.port)
        endpoint = self.endpoint.lstrip("/")

        return f"{base_url}/{endpoint}"

    def _request(self, url: str) -> requests.Response:
        query = self._get_formatted_query()

        try:
            return requests.get(
                url,
                data=query,
                headers={
                    "Content-Type": "application/json",
                },
            )
        except Exception:
            print_err("There was an error making the request")

            raise

    def _get_formatted_query(self) -> str:
        return json.dumps(self.query, indent=2)


@command()
@option("--host", "-h", help="where ES is hosted", required=True, type=STRING)
@option("--port", "-p", help="ES's port", required=False, type=STRING, default="")
@option("--endpoint", "-e", "endpoint", help="Endpoint to use", required=True, type=STRING)
@option("--pretty", help="Pretty print JSON response", default=False, is_flag=True)
def cli(**kwargs):
    ElasticSearchCommand(**kwargs).run()


if __name__ == "__main__":
    cli()

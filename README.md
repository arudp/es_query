# es_query
Command to run an ElasticSearch query from the command line.

Deps to install with pip3:
```
pip3 install --upgrade pip && pip3 install click requests
```

Pipe the query through the `stdin` (e.g., `cat file` or `echo`) and run it:
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

You can also add an executable to your `PATH`:
```
#!/bin/bash

PYTHONPATH=/path/to/python3/bin python3 /path/to/es.py $@
```


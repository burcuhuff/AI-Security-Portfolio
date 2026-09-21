# DEMO

Install dependencies:
```
python -m pip install -r requirements.txt
```

Run as an analyst with search and read access:
```
DEMO_USER=analyst python -m client.agent
```

Run as a restricted user with search-only access:
```
DEMO_USER=restricted_user python -m client.agent
```

The restricted user can discover matching documents but is denied access to
document contents.


### Tests

Run the security tests with:
```
python -m pytest -q
```
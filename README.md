# GoreeCloud GitHub Shared Workflows

**Status: first-party repository-maintenance tooling; not a deployed GoreeCloud application.**

This repository holds shared GitHub Actions workflows, bounded editorial-advisory scripts and internal development governance for the public GoreeCloud repositories. The authoritative project policies remain in the founder's GoreeCloud Google Drive; repository content is subordinate to those instructions.

## Included tooling

- [Shared SlopMonster advisory](docs/slopmonster-advisory.md) is a non-blocking writing-pattern review and **not** a security scan or proof of AI authorship. Its reusable workflow fetches the external SlopMonster scorer separately at a reviewed commit; upstream scorer source is **not** vendored in this repository.
- [GoreeCloud advisory adapter](scripts/slopmonster_advisory.py) is original bounded Python tooling for the shared review, with [synthetic tests](tests/test_slopmonster_advisory.py).
- [Autonomous repository development guidance](docs/autonomous-repository-development.md) describes proposed workflows but does not grant elevated permissions or bypass branch protections.

The scanner evaluates tracked prose in a read-only manner. Its results may be unavailable or incomplete; a green non-blocking job is **not** evidence that the scanner actually ran or that findings were cleared.

## Local verification

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile scripts/slopmonster_advisory.py
```

## License and provenance

The first-party GoreeCloud-authored repository source and documentation are licensed under the [MIT License](LICENSE), copyright (c) 2026 GoreeCloud. External SlopMonster source remains owned and separately licensed by its original authors and is downloaded only through the reviewed CI checkout. Other providers' GitHub Actions retain their own licenses and terms.

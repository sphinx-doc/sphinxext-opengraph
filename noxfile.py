"""Configuration to automatically run jobs and tests via `nox`.

For example, to build the documentation with a live server:

  nox -s docs -- live

List available jobs:

  nox -l

ref: https://nox.thea.codes/
"""

from __future__ import annotations

import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session
def docs(session: nox.Session) -> None:
    """Build the documentation. Use `-- live` to build with a live server."""
    session.install('--group', 'docs')
    session.install('-e', '.')
    common_args = '-M', 'html', 'docs', 'docs/build'
    if 'live' in session.posargs:
        session.install('ipython')
        session.install('sphinx-autobuild')
        session.run('sphinx-autobuild', *common_args)
    else:
        session.run('sphinx-build', *common_args, '-nW', '--keep-going')


@nox.session
def test(session: nox.Session) -> None:
    """Run the test suite."""
    session.install('-e', '.')
    session.install('--group', 'test')
    session.run('pytest', *session.posargs)

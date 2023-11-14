import os

import nox

# default sessions that shall be run
nox.options.sessions = ["lint_pylint", "lint_flake8"]

EDITABLE_TESTS = True
PYTHON_VERSIONS = None
if "GITHUB_ACTIONS" in os.environ:
    PYTHON_VERSIONS = ["3.11"]
    EDITABLE_TESTS = False

@nox.session
def lint_flake8(session):
    session.install("-e", ".[lint_flake8]")
    session.run("flake8", "newground")

@nox.session
def lint_pylint(session):
    session.install("-e", ".[lint_pylint]")
    session.run("pylint", "newground")    

@nox.session
def format(session):
    session.install("-e", ".[format]")
    check = "check" in session.posargs

    autoflake_args = [
        "--in-place",
        "--imports=fillname",
        "--ignore-init-module-imports",
        "--remove-unused-variables",
        "-r",
        "newground",
    ]
    if check:
        autoflake_args.remove("--in-place")
    session.run("autoflake", *autoflake_args)

    isort_args = ["--profile", "black", "newground"]
    if check:
        isort_args.insert(0, "--check")
        isort_args.insert(1, "--diff")
    session.run("isort", *isort_args)

    black_args = ["newground"]
    if check:
        black_args.insert(0, "--check")
        black_args.insert(1, "--diff")
    session.run("black", *black_args)
    

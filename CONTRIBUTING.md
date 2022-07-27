# Contributing

## Report Bugs

Report bugs at [<https://github.com/udl-ai/udlai/issues>](<https://github.com/udl-ai/udlai/issues>).

If you are reporting a bug, please include:

* Detailed steps to reproduce the bug.
* Minimal reproducible example

## Get Started

Ready to contribute? Here's how to set up `udlai` for local development.

1. Clone the repository locally:

```sh
git clone https://github.com/udl-ai/udlai.git
```

1. Create a conda environment

Ideally, you should always create a fresh environment for new project, unless you are
certain you can manage environments yourself. There is an `environment.yml` file that
should help you.

```sh
cd udlai
conda env create -f environment.yml
```

This will create a new development environment called `udlai_env`
with all required dependencies. You can now activate the environment.

```sh
conda activate udlai_env
```

1. Install the package in an editable way

Install the package to the environment with the `-e` flag to keep it editable.

```sh
pip install -e .
```

1. install pre-commit

Pre-commit ensures that your code follows `black`, `flake8` and `isort` standards.

```sh
pre-commit install
```

It is highly recommended to set-up your IDE to check for these formatting styles for you.
The CI will fail if the commit does not adhere. You can also enforce the style manually.

```sh
black udlai
flake8 udlai
isort udlai
```

1. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

Now you can make your changes locally.

1. Run tests

Once ready, run the complete unit tests.

```sh
pytest -v udlai --cov=udlai --cov-fail-under=95 --cov-report term-missing
```

The command will also report code coverage and fail if it is under 95%.
Ensure that 100% of your code is tested unless there is a good reason not to. You can
also change the threshold manually in the command with `--cov-fail-under=` flag.
Coverage check also reports lines that are not covered as `Missing`.

1. Commit your changes and push your branch to Github:

```sh
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

1. Submit a pull request through the Github website.

##  Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. All tests pass.
4. Code follows `black`, `flake8` and `isort` style rules.

## Documentation

Documentation lives in the `docs` folder and is (mostly) automatically generated via
`sphinx`. To generate a new version of docs, navigate to the folder and use a Makefile
to clean previous versions and build a new one.

```sh
cd docs
make clean
make html
```

The documentation is generated in `build/html` and automatically deployed to
readthedocs.

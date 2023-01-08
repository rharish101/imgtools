# imgtools

**Unmaintained**: I've switched to using [Czkawka](https://github.com/qarmin/czkawka).

This is a collection of ~~hacky scripts~~ tools for images, intended for my personal use.
Currently this consists of:

- hash: Compute the [difference hash (d-hash)](https://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html) of an image.
- diff: Compare two images using [SSIM](https://en.wikipedia.org/wiki/Structural_similarity).
- rmdup: Delete all duplicate images in a directory.

## Instructions

All tools are collected inside one module called `imgtools`.
This uses argparse to parse commandline arguments, and sub-parsers for each tool.

To run a tool *mytool*, type:
```sh
imgtools mytool [args]...
```

For viewing the usage for a tools *mytool*, type:
```sh
imgtools mytool --help
```

For viewing the usage for the module itself, type:
```sh
imgtools --help
```

## Setup

[Poetry](https://python-poetry.org/) is used for conveniently installing and managing dependencies.

1. *[Optional]* Create and activate a virtual environment with Python >= 3.9.

2. Install Poetry globally (recommended), or in a virtual environment.
    Please refer to [Poetry's installation guide](https://python-poetry.org/docs/#installation) for recommended installation options.

    You can use pip to install it:
    ```sh
    pip install poetry
    ```

3. Install all dependencies with Poetry:
    ```sh
    poetry install --no-dev
    ```

    If you didn't create and activate a virtual environment in step 1, Poetry creates one for you and installs all dependencies there.
    To use this virtual environment, run:
    ```sh
    poetry shell
    ```

### For Contributing

[pre-commit](https://pre-commit.com/) is used for managing hooks that run before each commit, to ensure code quality and run some basic tests.
Thus, this needs to be set up only when one intends to commit changes to git.

1. Activate the virtual environment where you installed the dependencies.

2. Install all dependencies, including extra dependencies for development:
    ```sh
    poetry install
    ```

3. Install pre-commit hooks:
    ```sh
    pre-commit install
    ```

**NOTE**: You need to be inside the virtual environment where you installed the above dependencies every time you commit.

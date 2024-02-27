Installation
=============

This section provides instructions on how to install the `raspidevkit` package.

Install using pip
-----------------------

The recommended way to install `raspidevkit` is using `pip`, Python's package manager. To install `raspidevkit`, simply run the following command in your terminal:

.. code-block:: shell

    pip install raspidevkit

This will download and install the latest version of `raspidevkit` from the Python Package Index (PyPI) along with any necessary dependencies.

Install from source
------------------------

Alternatively, you can install `raspidevkit` from the source code available on GitHub. First, clone the GitHub repository to your local machine:

.. code-block:: shell

    git clone https://github.com/raspidevkit/raspidevkit.git

Before continuing make sure that build dependencies are installed in your system

.. code-block::shell

    pip install setuptools wheel

Once you've cloned the repository, navigate to the `raspidevkit` directory and run the following command to install the package:

.. code-block:: shell

    python setup.py sdist bdist_wheel
    pip install dist/raspidevkit-{version}.tar.gz
    # replace {version} with the current version of raspidevkit

This will install `raspidevkit` from the local source files.

Verification
------------

To verify that `raspidevkit` has been installed correctly, you can try importing it in a Python shell or script:

.. code-block:: python

    import raspidevkit

If no errors occur, the installation was successful.

Congratulations! You've successfully installed `raspidevkit` on your system.

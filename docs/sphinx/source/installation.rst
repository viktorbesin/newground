.. _installation-reference:

Installation Guide
============================================

By following this guide you will be able to install the newground prototype.

Requirements
------------

In addition to the the pip-packages listed below, it is necessary to have Python3 installed, where we support python versions *>=3.11*.

PIP-Packages Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^
* clingo>=5.6.2
* clingox
* networkx
* future-fstrings

General Installation
-----------------------


For using the newground prototype an installation is not required, but recommended, as all dependencies are automatically installed.

General Installation Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can install the prototype by typing the following command in your CLI:

First check your python version (should be **>=3.11**):

.. code-block:: console

    $ python --version

Then install the prototype:

.. code-block:: console

    $ python -m pip install .

Check the installation:

.. code-block:: console

    $ newground --help

Which output should be:

.. code-block:: console

    $ newground --help
    usage: newground [files]

    positional arguments:
      files

    options:
      -h, --help            show this help message and exit
      --no-show             Do not print #show-statements to avoid compatibility issues.
      --mode {rewrite-aggregates-ground-partly,rewrite-aggregates-no-ground,rewrite-aggregates-ground-fully}
      --aggregate-strategy {RA,RS,RS-PLUS,RS-STAR,RECURSIVE}
      --cyclic-strategy {assume-tight,level-mappings,shared-cycle-body-predicates,level-mappings-AAAI}


General Installation via make
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have the *make* environment installed, you can use it to install newground.
To install the general version, execute the following command.

.. code-block:: console

    $ make install

Check if newground was correctly installed:

.. code-block:: console

    $ newground --help
    usage: newground [files]

    positional arguments:
      files

    options:
      -h, --help            show this help message and exit
      --no-show             Do not print #show-statements to avoid compatibility issues.
      --mode {rewrite-aggregates-ground-partly,rewrite-aggregates-no-ground,rewrite-aggregates-ground-fully}
      --aggregate-strategy {RA,RS,RS-PLUS,RS-STAR,RECURSIVE}
      --cyclic-strategy {assume-tight,level-mappings,shared-cycle-body-predicates,level-mappings-AAAI}



Uninstall
---------

Although we would be very sad, if you would do it, you can uninstall Newground with the following command:

.. code-block:: console

    $ python -m pip uninstall newground

Or by using make:

.. code-block:: console

    $ make uninstall

Installation for development
----------------------------

We provide several different options for installation for specific purposes, 
which effectively means that you install additional dependencies that are not required for the prototype, 
but for development.
This includes dependencies for code-linting, documentation and formatting.

Installation for Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can install the additional dependencies for installation by:

.. code-block:: console

    $ python -m pip install .[doc]

Or use the Makefile:

.. code-block:: console

    $ make install-doc

When installed you are able to compile the documentation via Sphinx.
For doing this navigate to *docs/sphinx* and enter:

.. code-block:: console

    docs/sphinx$ sphinx-build -M html source/ build/

The resulting documentation is placed in the build folder.
You can see a local preview of the documentation page by using a simple local http-server, which you can do e.g. by:

.. code-block:: console

    docs/sphinx/build/html$ python -m http.server

Autoformatting/Linting - Installing nox
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

nox_ environments are used for linting and autoformatting.
Therefore we recommend you to install nox for these purposes.
This can be done in the following way:

.. code-block:: console

    $ python -m pip install nox

Autoformatting with nox
""""""""""""""""""""""""

For autoformatting the newground directory, use:

.. code-block:: console

    $ nox -s format

Linting with nox
""""""""""""""""

We lint with two linters: Pylint_ and Flake8_. 
For linting with Pylint enter:

.. code-block:: console

    $ nox -s lint_pylint

For linting with Flake8 enter:

.. code-block:: console

    $ nox -s lint_flake8


Installation for Autoformatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is not recommended to use the autoformatter directly!
We recommend using the autoformatter with nox_, e.g. by:

.. code-block:: console

    $ nox -s format

If you want to do it manually, you can install the dependencies for the autoformatter by entering the following command:

.. code-block:: console

    $ python -m pip install .[format]

Or use the Makefile:

.. code-block:: console

    $ make install-format

Installation for Linting
^^^^^^^^^^^^^^^^^^^^^^^^

It is not recommended to directly use the linters, but use nox_ instead.
Therefore, for linting with Pylint enter:

.. code-block:: console

    $ nox -s lint_pylint

For linting with Flake8 enter:

.. code-block:: console

    $ nox -s lint_flake8

But if you still want to install the linters, you can do this in the following way.

Install Dependencies for Pylint
""""""""""""""""""""""""""""""""

.. code-block:: console

    $ python -m pip install .[lint_pylint]

Or use the Makefile:

.. code-block:: console

    $ make install-lint-pylint

Install Dependencies for Flake8
""""""""""""""""""""""""""""""""

.. code-block:: console

    $ python -m pip install .[lint_flake8]

Or use the Makefile:

.. code-block:: console

    $ make install-lint-flake8

Install Everything
------------------

If you have make installed and want to install all dependencies,
you can do this with:

.. code-block:: console

    $ make install-all


Direct Usage without Installation
---------------------------------

Although an installation is generally recommended, it is possible to directly start the prototype with a Python script, without explicitly installing the prototype.
For this first install the requirements with:

.. code-block:: console

    $ python -m pip install -r requirements.txt


And then directly call the prototype script:

.. code-block:: console
    
    $ python start_newground.py --help
    usage: newground [files]

    positional arguments:
      files

    options:
      -h, --help            show this help message and exit
      --no-show             Do not print #show-statements to avoid compatibility issues.
      --mode {rewrite-aggregates-ground-partly,rewrite-aggregates-no-ground,rewrite-aggregates-ground-fully}
      --aggregate-strategy {RA,RS,RS-PLUS,RS-STAR,RECURSIVE}
      --cyclic-strategy {assume-tight,level-mappings,shared-cycle-body-predicates,level-mappings-AAAI}


.. _nox: https://nox.thea.codes/en/stable/
.. _Pylint: https://pypi.org/project/pylint/
.. _Flake8: https://flake8.pycqa.org/en/latest/


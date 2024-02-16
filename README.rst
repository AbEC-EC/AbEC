Review checklist
---------------

General checks
==============

- [X] Repository: Is the source code for this software available at the repository url?

- [X] License: Does the repository contain a plain-text LICENSE file with the contents of an OSI approved software license?

- [X] Contribution and authorship: Has the submitting author made major contributions to the software? Does the full list of paper authors seem appropriate and complete?


Functionality
=============

- [X] Installation: Does installation proceed as outlined in the documentation?

   - [ ] Modificar a pagina de instalacao para ter uma instalacao mais manual.

- [ ] Functionality: Have the functional claims of the software been confirmed?

   - [ ] Listar as funcionalidades
   - [ ] Confirm the functional claims

- [X] Performance: If there are any performance claims of the software, have they been confirmed? (If there are no claims, please check off this item.)


Documentation
=============

- [ ] A statement of need: Do the authors clearly state what problems the software is designed to solve and who the target audience is?

- [X] Installation instructions: Is there a clearly-stated list of dependencies? Ideally these should be handled with an automated package management solution.

- [X] Example usage: Do the authors include examples of how to use the software (ideally to solve real-world analysis problems).

- [ ] Functionality documentation: Is the core functionality of the software documented to a satisfactory level (e.g., API method documentation)?

- [ ] Automated tests: Are there automated tests or manual steps described so that the functionality of the software can be verified?

- [ ] Community guidelines: Are there clear guidelines for third parties wishing to 1) Contribute to the software 2) Report issues or problems with the software 3) Seek support


Software paper
==============

- [ ] Summary: Has a clear description of the high-level functionality and purpose of the software for a diverse, non-specialist audience been provided?

- [ ] A statement of need: Does the paper have a section titled ‘Statement of need’ that clearly states what problems the software is designed to solve, who the target audience is, and its relation to other work?

- [ ] State of the field: Do the authors describe how this software compares to other commonly-used packages?

- [ ] Quality of writing: Is the paper well written (i.e., it does not require editing for structure, language, or writing quality)?

- [ ] References: Is the list of references complete, and is everything cited appropriately that should be cited (e.g., papers, datasets, software)? Do references in the text use the proper citation syntax?


|logo|

AbEC is a Component-based Framework for Research and Development in Static and Dynamic Evolutionary Computation 

|Build status| |Coverage Status| 

Documentation
-------------

|Documentation Status|

The documentation for ``AbEC`` is hosted on `Read the docs
<https://abec-ec.github.io>`__.

Installation and Dependencies
-----------------------------

The easiest way to get AbEC is to install cloning the reposity from github.

The recommended install method is to use ``git clone``::

   git clone https://github.com/AbEC-EC/AbEC.git

See the `installation
instructions <https://abec-ec.github.io/install.html>`_ in the
`documentation <https://abec-ec.github.io/>`__ for more information.

Attribution
-----------

|JOSS| |DOI|

If you make use of this code, please cite the `JOSS <http://joss.theoj.org>`_
paper::

    @article{abec,
      doi = {xx.xxxxxxx/joss.xxxxx},
      url = {https://doi.org/xx.xxxxxx/joss.xxxxx},
      year = 2024,
      month = {xxx},
      publisher = {The Open Journal},
      volume = {x},
      number = {xx},
      author = {Alexandre Mascarenhas},
      title = {AbEC - Adjustable Evolutionary Components: A Component-based Framework for Research and Development in Static and Dynamic Evolutionary Computation },
      journal = {The Journal of Open Source Software}
    }

Please also cite the Zenodo DOI |DOI| as a software citation - see the
`documentation
<https://abec-ec.github.io>`_ for up
to date citation information.

License
-------

|License|

Copyright 2024 Alexandre Mascarenhas and contributors.

``AbEC`` is free software made available under the MIT License. For details see
the `LICENSE <https://github.com/AbEC-EC/AbEC/blob/main/LICENCE>`_ file.

.. |License| image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat
   :target: https://github.com/AbEC-EC/AbEC/blob/main/LICENCE
.. |Documentation Status| image:: https://readthedocs.org/projects/abec/badge/?version=latest
   :target: https://abec.readthedocs.io/en/latest/?badge=latest
.. |JOSS| image:: 
   :target: 
.. |ASCL| image:: https://img.shields.io/badge/ascl-1707.006-blue.svg?colorB=262255
   :target: http://ascl.net/1707.006
.. |logo| image:: https://github.com/AbEC-EC/AbEC/blob/main/docs/abec-logo2-nb.png
   :target: https://github.com/AbEC-EC/AbEC
   :width: 400
.. |check| raw:: html
    <input checked=""  type="checkbox">
.. |check_| raw:: html
    <input checked=""  disabled="" type="checkbox">
.. |uncheck| raw:: html
    <input type="checkbox">
.. |uncheck_| raw:: html
    <input disabled="" type="checkbox">


Contributors
------------

See the `AUTHORS.rst <https://github.com/AbEC-EC/AbEC/blob/main/AUTHORS.rst>`_
file for a complete list of contributors to the project.


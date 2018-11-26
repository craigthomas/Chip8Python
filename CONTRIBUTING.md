# Contributing

First of all, thank you for considering making a contribution to the project! Below are some guidelines for contributing 
to the project. Please feel free to propose changes to the guidelines in a pull request if you feel something is missing
or needs more clarity.

# Table of Contents

1. [How can I contribute?](#how-can-i-contribute)
    1. [Reporting bugs](#reporting-bugs)
    2. [Suggesting features](#suggesting-features)
    3. [Contributing code](#contributing-code)
    4. [Pull requests](#pull-requests)
2. [Style guidelines](#style-guidelines)
    1. [Git commit messages](#git-commit-messages)
    2. [Code style](#code-style)

# How can I contribute?

There are several different way that you can contribute to the development of the project, each of which are most 
welcome.

## Reporting bugs

Bugs are reported through the [GitHub Issue](https://github.com/craigthomas/Chip8Python/issues) interface. Please check
first to see if the bug you are reporting has already been reported. When reporting a bug, please take the time to 
describe the following details:

1. **Descriptive Title** - please ensure that the title to your issue is clear and descriptive of the problem. 
2. **Steps for Reproduction** - outline all the steps exactly that are required to reproduce the bug. For example,
start by explaining how you started the program, which ROM you were running, and any other command line switches
that were set, as well as what environment you are running in (e.g. Windows, Linux, MacOS, etc). 
3. **Describe the Bug Behaviour** - describe what happens with the emulator, and why you think that this behaviour
represents a bug. 
4. **Describe Expected Behaviour** - describe what behaviour you believe should occur as a result of the steps
that you took up to the point where the bug occurred.

Please feel free to provide additional context to help a developer track down the bug:

* **Can you reproduce the bug reliably or is it intermittent?** If it is intermittent, please try to explain what 
would normally provoke the bug, or under what conditions you saw it occur last time.
* **Does it happen for any other ROMs?** It is helpful if you can try and pinpoint the buggy behaviour to a certain
ROM or handful of ROMs. 

## Suggesting features

When suggesting features or enhancements for the emulator, it is best to check out the open issues first to see whether
or not such a feature is already under development. It is also worthwhile checking any open branches to see if the 
feature you are requesting is already in development. Finally, before submitting your suggestion, please ensure that 
the feature does not already exist by updating your local copy with the latest version from our `master` branch.

To submit a feature request, please open a new [GitHub Issue](https://github.com/craigthomas/Chip8Python/issues) and
provide the following details:

1. **Descriptive Title** - please ensure that the title to your issue is clear and descriptive of the enhancement or
functionality you wish to see.
2. **Step by Step Description** - describe how the functionality of the system should occur with a step-by-step breakdown
of how you expect the emulator to run. For example, if you wish to have a new debugging key added, describe how the
emulator execution flow will change when the key is pressed. 
3. **Use Animated GIFs** - if you are feeling ambitious, or if you feel words do not adequately describe the proposed
functionality, please submit an animated GIF, or a drawing of the new proposed functionality.
4. **Explain Usefulness** - please take a brief moment to describe why you feel the new functionality would be useful.

## Contributing code

Code contributions should be made using the following process:

1. **Fork the Repository** - create a fork of the respository using the Fork button in GitHub.
2. **Make Code Changes** - using your forked repository, make changes to the code as you see fit. We recommend creating a
branch for your code changes so that you can easily update your own local master without creating too many merge 
conflicts.
3. **Submit Pull Request** - when you are ready, submit a pull request back to the `master` branch of this repository.
The pull request will be reviewed, and you may be asked questions about the changes you are proposing. In some cases,
we may ask you to make adjustments to the code to fit in with the overall style and behavioiur of the rest of the
project. 

There are also some additional guidelines you should follow when coding up enhancements or bugfixes:

1. Please reference any open issues that the Pull Request will close by writing `Closes #` with the issue number (e.g. `Closes #12`).
2. New functionality should have unit and/or integration tests that exercise at least 50% of the code that was added. 
3. For bug fixes, please ensure that you have a test that covers buggy input conditions so that we reduce the likelihood of 
a regression in the future. 
4. Please ensure all functions have appropriately descriptive docstrings, as well as descriptions for inputs and outputs. 

If you don't know where to start, then take a look for issues marked `beginner` or `help-wanted`. Any issues with the `beginner` tag
will generally only require one or two lines of code to fix. Issues marked `help-wanted` may be more complex than beginner issues,
but should be scoped in such a way to ease you in to the codebase.

## Pull requests

Please follow all the instructions as mentioned in the Pull Request template. When you submit your pull request, please ensure that 
all of the required [status checks](https://help.github.com/articles/about-status-checks/) have succeeded. If the status checks
are failing, and you believe that the failures are not related to your change, please leave a description within the pull request why
you believe the failures are not related to your code changes. A maintainer will re-run the checks manually, and investigate further.

A maintainer will review your pull request, and may ask you to perform some additional design work, tests, or other changes prior
to approving and merging your code. 

# Style guidelines

In general, there are two sets of style guidelines that we ask contributors to follow.

## Git commit messages

* For large changesets, provide detailed descriptions in your commit logs regarding what was changed. The git commit message should
look like this:

    ```
    $ git commit -m "A brief title / description of the commit
    >
    > A more descriptive set of paragraphs about the changeset."
    ```
    
* Limit your first line to 70 characters.
* If you are just changing documentation, please include `[ci skip]` in the commit title.
* Please reference issue numbers and pull requests in the commit description where applicable using `#` and the issue number (e.g.
`#24`).

## Code style

* Please follow the [PEP 8 Style Guidelines](https://www.python.org/dev/peps/pep-0008/) for any code that you wish to contribute.
* When submitting code, we strongly suggesting running [pylint](https://www.pylint.org/) on any file that you changed to see
if there are any problems introduced to the codebase.
* Please ensure any docstrings describe the functionality of the functions, including what the input and output parameters
do.
* Please do not use docstrings on unit test functions (these get displayed by the test runner instead of the name of the function). 
Instead, use descriptive names for the functions (e.g. `test_cpu_raises_nmi_when_overflow_occurs`).
* When importing, we prefer the following layout:
    * Full package imports at the top (e.g. `import os`).
    * Selective function imports using `from` next (e.g. `from os import chdir`).
    * Local imports last.

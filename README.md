# arcos-gui

[![License](https://img.shields.io/pypi/l/arcos-gui.svg?color=green)](https://github.com/bgraedel/arcos-gui/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/arcos-gui.svg?color=green)](https://pypi.org/project/arcos-gui)
[![Python Version](https://img.shields.io/pypi/pyversions/arcos-gui.svg?color=green)](https://python.org)
[![tests](https://github.com/bgraedel/arcos-gui/workflows/tests/badge.svg)](https://github.com/bgraedel/arcos-gui/actions)
[![codecov](https://codecov.io/gh/bgraedel/arcos-gui/branch/main/graph/badge.svg)](https://codecov.io/gh/bgraedel/arcos-gui)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/arcos-gui)](https://napari-hub.org/plugins/arcos-gui)

A napari plugin to detect and visualize collective signalling events

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

## Installation

prior to installing arcos-gui it requires a working R installation with the ARCOS libary github.com/dmattek/ARCOS installed.

You can install `arcos-gui` via [pip]:

    pip install arcos-gui

## OS Support
This package relies on a library called rpy2 that allows exection of R function within python code. It officially only supports UNIX based systems (Linux, MacOS).
For Windows users to get it to work requires adding a Path system environment variable that points to the R binary.

To install latest development version :

    pip install git+https://github.com/bgraedel/arcos-gui.git

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"arcos-gui" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/bgraedel/arcos-gui/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

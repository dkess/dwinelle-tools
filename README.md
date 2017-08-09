This is all of the code I wrote that was useful in creating Dwinelle Navigator.  The website's code is in the `web/` directory, Python code is in the `video/` directory (some scripts require SymPy), and mpv scripts written in lua are in the `luatest/` directory.

To build the web interface, clone the repo, update submodules (`git submodule update --init --recursive`), and run `make`. Serve from the `web/` directory.

All code is licensed under GPLv3.  The graph of Dwinelle, including the locations of rooms (soon to be uploaded), is licensed under the [Open Database License (ODbL)](http://opendatacommons.org/licenses/odbl/1.0/).

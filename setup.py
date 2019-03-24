__author__ = "Omer Yampel @yampelo"

import io
import os
import sys
from shutil import rmtree
from setuptools import find_packages, setup, Command


# Package meta-data.
NAME = "Beagle"
DESCRIPTION = "Beagle is an incident response and digital forensics tool which transforms data sources and logs into graphs"
URL = "https://github.com/yampelo/beagle"
AUTHOR = "yampelo"
REQUIRES_PYTHON = ">=3.6.0,<3.7"
VERSION = "1.0.0"
EMAIL = None


EXTRAS = None
REQUIRED = [
    "acora==2.0",
    "aff4-snappy==0.5.1",
    "ansimarkup==1.4.0",
    "appnope==0.1.0 ; sys_platform == 'darwin'",
    "arrow==0.10.0",
    "artifacts==20170909",
    "atomicwrites==1.3.0",
    "attrs==19.1.0",
    "backcall==0.1.0",
    "better-exceptions-fork==0.2.1.post6",
    "certifi==2019.3.9",
    "chardet==3.0.4",
    "click==7.0",
    "colorama==0.4.1",
    "coverage==5.0a4",
    "decorator==4.4.0",
    "expiringdict==1.1.4",
    "filelock==2.0.6",
    "flask-sqlalchemy==2.3.2",
    "flask==1.0.2",
    "future==0.16.0",
    "grpcio==1.17.1",
    "gunicorn==19.9.0",
    "hexdump==3.3",
    "html5lib==1.0.1",
    "httplib2==0.9.2",
    "idna==2.5",
    "intervaltree==2.1.0",
    "ipaddr==2.2.0",
    "ipython-genutils==0.2.0",
    "ipython==6.5.0",
    "isodate==0.6.0",
    "itsdangerous==1.1.0",
    "jedi==0.13.3",
    "jinja2==2.10",
    "loguru==0.2.5",
    "lxml==4.3.2",
    "markupsafe==1.1.1",
    "more-itertools==6.0.0 ; python_version > '2.7'",
    "neo4j==1.7.2",
    "neobolt==1.7.4",
    "neotime==1.7.4",
    "networkx==2.2",
    "oauth2client==3.0.0",
    "parsedatetime==2.4",
    "parso==0.3.4",
    "pathlib==1.0.1",
    "pexpect==4.6.0 ; sys_platform != 'win32'",
    "pickleshare==0.7.5",
    "pluggy==0.9.0",
    "portpicker==1.1.1",
    "prompt-toolkit==1.0.15",
    "protobuf==3.6.1",
    "psutil==5.6.1",
    "ptyprocess==0.6.0",
    "py==1.8.0",
    "pyaff4==0.26.post6",
    "pyasn1-modules==0.2.4",
    "pyasn1==0.4.5",
    "pyblake2==0.9.3",
    "pycryptodome==3.4.7",
    "pydgraph==1.0.1",
    "pyelftools==0.24",
    "pygments==2.3.1",
    "pyparsing==2.1.5",
    "pytest-cov==2.6.1",
    "pytest==4.3.1",
    "python-dateutil==2.6.1",
    "python-evtx==0.6.1",
    "pytsk3==20170802",
    "pytz==2017.3",
    "pyyaml==3.12",
    "rdflib[sparql]==4.2.2",
    "readline==6.2.4.1",
    "rekall-agent==1.7.1",
    "rekall-capstone==3.0.5.post2",
    "rekall-core==1.7.2rc1",
    "rekall-efilter==1.6.0",
    "rekall-lib==1.7.2rc1",
    "rekall-yara==3.6.3.1",
    "rekall==1.7.2rc1",
    "requests==2.18.1",
    "rsa==4.0",
    "simplegeneric==0.8.1",
    "six==1.12.0",
    "sortedcontainers==1.5.7",
    "sparqlwrapper==1.8.2",
    "sqlalchemy==1.3.1",
    "sseclient==0.0.18",
    "traitlets==4.3.2",
    "urllib3==1.21.1",
    "wcwidth==0.1.7",
    "webencodings==0.5.1",
    "werkzeug==0.14.1",
]

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.

about = {}  # type: ignore

if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []  # type: ignore

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["test*", "beagle/web"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Security",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
    ],
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)

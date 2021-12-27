from itertools import chain
from setuptools import setup, find_packages


VERSION_FILE = "cv2PySide6/version.py"

def get_version():
    with open(VERSION_FILE, "r") as f:
        exec(compile(f.read(), VERSION_FILE, 'exec'))
    return locals()["__version__"]


def read_requirements(path):
    with open(path, "r") as f:
        ret = f.read().splitlines()
    return ret


def get_extras_require():
    ret = {}

    ret["test"] = read_requirements("requirements/test.txt")
    ret["test-ci"] = read_requirements("requirements/test.txt") \
                     + read_requirements("requirements/test-ci.txt")
    ret['full'] = list(set(chain(*ret.values())))
    return ret


setup(
    name="cv2PySide6",
    version=get_version(),
    python_requires='>=3.9',
    description="Package for video display by OpenCV-Python and PySide6",
    author="Jisoo Song",
    author_email="jeesoo9595@snu.ac.kr",
    url="https://github.com/JSS95/cv2PySide6",
    packages=find_packages(),
    install_requires=read_requirements("requirements/install.txt"),
    extras_require=get_extras_require(),
)

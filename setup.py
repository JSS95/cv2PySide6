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


setup(
    name="cv2PySide6",
    version=get_version(),
    python_requires='>=3.9',
    description="Package for video display by OpenCV-Python and PySide6",
    author="Jisoo Song",
    author_email="jeesoo9595@snu.ac.kr",
    packages=find_packages(),
    install_requires=read_requirements("requirements/install.txt"),
)

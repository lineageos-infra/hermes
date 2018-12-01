import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = fh.read().split()
setuptools.setup(
    name="hermes",
    version="0.0.1",
    description="Slack RTM Framework",
    url="https://github.com/lineageos/infra/hermes.git",
    author_email="infra@lineageos.org",
    author="LineageOS Infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"hermes": "hermes"},
    packages=setuptools.find_packages(),
    classifiers=("Programming Language :: Python 3"),
    install_requires=requirements,
)

import setuptools

import versioneer

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="udlai",
    author="Martin Fleischmann",
    author_email="m.fleischmann@urbandatalab.net",
    python_requires=">=3.8",
    description="UDL.AI Python interface",
    install_requires=["numpy", "pandas"],
    long_description=long_description,
    include_package_data=True,
    packages=setuptools.find_packages(include=["udlai", "udlai.*"]),
    url="https://github.com/udl-ai/udlai",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)

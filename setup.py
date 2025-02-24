from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="loadhouse",
    version="0.1.4",
    author="Flynn",
    description="A data loading and transformation engine for data lakehouses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flynn/loadhouse",
    packages=find_packages(include=['loadhouse', 'loadhouse.*']),
    package_data={'loadhouse': ['*', '*/*', '*/*/*', '*/*/*/*']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pyspark==3.5.0",
        "delta-spark==3.2.0",
        "great-expectations==0.18.8"
    ],
    include_package_data=True
)
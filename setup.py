import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-climate-health-toolbox",
    version="0.0.2",
    author="Climate and Health Research Group - Unicamp",
    author_email="paulad@unicamp.br",
    description="Toolbox to study the impact of climate extremes in health",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/climate-and-health-datasci-Unicamp/py-climate-health-toolbox",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.6',
)

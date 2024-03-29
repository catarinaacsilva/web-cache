import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webcache",
    version="0.0.3",
    author="Catarina Silva",
    author_email="c.alexandracorreia@ua.pt",
    description="Web cache library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/catarinaacsilva/web-cache",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['selenium>=3.141.0', 'requests>=2.22.0', 'beautifulsoup4>=4.8.1'],
)
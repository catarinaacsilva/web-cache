import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webcache",
    version="0.0.2",
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
    dependency_links=['git+https://github.com/catarinaacsilva/check-https-utils.git#egg=check_https_utils'],
    install_requires=['selenium>=3.141.0', 'requests>=2.22.0', 'check_https_utils'],
)
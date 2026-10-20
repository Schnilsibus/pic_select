import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name="pic_select",
    version="1.0.1",
    author="Nils Urbach",
    author_email="ndu01u@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=[],
    packages=setuptools.find_namespace_packages(where = ".", include = ["pic_select", "pic_select.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python"
    ],
    test_suite="tests",
)   
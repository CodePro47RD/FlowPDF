import os
from setuptools import setup, find_packages

readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="flowpdf",
    version="1.0.0",
    description="Open-source report generation library made in the Dominican Republic. Universal document engine and fluent report builder SDK for Python with native Rust Core, vector charts, custom TTF fonts, and WebAssembly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Edwin Abreu, Felix R. Benzan & FlowPDF Contributors",
    url="https://codepro47rd.github.io/FlowPDF/",
    packages=find_packages(),
    package_data={
        "flowpdf": [
            "runtimes/**/*",
            "runtimes/win-x64/native/*",
            "runtimes/linux-x64/native/*",
        ],
    },
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Printing",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Rust",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
)

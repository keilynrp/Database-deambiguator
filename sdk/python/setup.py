import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="ukip-universal-knowledge-intelligence-platform-client",
    version="1.0.0",
    description="A client library for accessing UKIP — Universal Knowledge Intelligence Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.11, <4",
    install_requires=["httpx >= 0.23.1, < 0.29.0", "attrs >= 22.2.0"],
    package_data={"ukip_universal_knowledge_intelligence_platform_client": ["py.typed"]},
)

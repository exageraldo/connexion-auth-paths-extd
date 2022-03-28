from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="connexion_auth_paths_extd",
    version="0.0.6",
    install_requires=[
        "connexion"
    ],
    extras_require={
        'aiohttp': "connexion[aiohttp]"
    }
)

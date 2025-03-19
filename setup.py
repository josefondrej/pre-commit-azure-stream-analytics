from setuptools import setup

setup(
    name="asa-auth-mode",
    version="0.1.0",
    py_modules=["asa_auth_mode"],
    entry_points={
        "console_scripts": ["asa-auth-mode=asa_auth_mode:main"],
    },
)

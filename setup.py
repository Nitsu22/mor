from setuptools import find_packages, setup


setup(
    name="morph-app",
    version="0.1.0",
    description="Desktop morph-analysis app prototype",
    packages=find_packages(),
    python_requires=">=3.9",
    extras_require={
        "mecab": [
            "mecab-python3>=1.0.9",
            "unidic-lite>=1.0.8",
        ],
        "gui": [
            "PySide6>=6.7",
        ],
        "build": [
            "pyinstaller>=6",
        ],
        "test": [
            "pytest>=8",
        ],
        "dev": [
            "mecab-python3>=1.0.9",
            "unidic-lite>=1.0.8",
            "PySide6>=6.7",
            "pyinstaller>=6",
            "pytest>=8",
        ],
    },
    entry_points={
        "console_scripts": [
            "morph-app=app.main:main",
        ],
    },
)

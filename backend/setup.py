from setuptools import setup, find_packages

setup(
    name="concept-visualizer-backend",
    version="0.1.0",
    description="Backend for the Concept Visualizer application",
    author="Concept Visualizer Team",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.110.0,<0.111.0",
        "uvicorn[standard]>=0.28.0,<0.29.0",
        "pydantic>=2.6.0,<2.7.0",
        "pydantic-settings>=2.2.0,<2.3.0",
        "httpx>=0.27.0,<0.28.0",
        "python-dotenv>=1.0.0,<1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0,<8.1.0",
            "pytest-asyncio>=0.23.0,<0.24.0",
            "black>=24.1.0,<24.2.0",
            "isort>=5.13.0,<5.14.0",
            "mypy>=1.7.0,<1.8.0",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
) 
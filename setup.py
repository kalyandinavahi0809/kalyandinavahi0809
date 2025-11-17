"""
Setup configuration for Network Signal Imputation ML Pipeline.
"""

from setuptools import setup, find_packages
import os

# Read version from file
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return '1.0.0'

# Read long description from README
def read_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_file, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='network-signal-imputation',
    version=read_version(),
    description='Production-ready ML pipeline for network signal imputation',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    author='ML Team',
    author_email='ml-team@company.com',
    url='https://github.com/kalyandinavahi0809/kalyandinavahi0809',
    license='MIT',
    
    # Package configuration
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    include_package_data=True,
    
    # Python version requirement
    python_requires='>=3.9,<3.12',
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.3.0',
            'pytest-cov>=4.0.0',
            'pytest-xdist>=3.2.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'pylint>=2.17.0',
            'mypy>=1.2.0',
            'isort>=5.12.0',
            'bandit>=1.7.0',
            'safety>=2.3.0',
        ],
        'docs': [
            'sphinx>=5.3.0',
            'sphinx-rtd-theme>=1.2.0',
            'sphinx-autodoc-typehints>=1.22.0',
        ],
        'notebook': [
            'ipython>=8.12.0',
            'jupyter>=1.0.0',
            'notebook>=6.5.0',
            'matplotlib>=3.7.0',
            'seaborn>=0.12.0',
        ],
    },
    
    # Entry points for CLI commands
    entry_points={
        'console_scripts': [
            'signal-imputation=modeling.pipeline:main',
            'feature-store-setup=feature_store.setup_feature_store:main',
            'model-register=modeling.registry:main',
            'quality-check=monitoring.quality_checks:main',
            'drift-detect=monitoring.drift_detection:main',
        ],
    },
    
    # Package classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    # Keywords for package discovery
    keywords=[
        'machine-learning',
        'ml-pipeline',
        'data-imputation',
        'network-signals',
        'snowflake',
        'feature-store',
        'model-registry',
        'mlops',
    ],
    
    # Project URLs
    project_urls={
        'Documentation': 'https://github.com/kalyandinavahi0809/kalyandinavahi0809/tree/main/docs',
        'Source': 'https://github.com/kalyandinavahi0809/kalyandinavahi0809',
        'Bug Reports': 'https://github.com/kalyandinavahi0809/kalyandinavahi0809/issues',
    },
    
    # Package data
    package_data={
        '': [
            'config.yaml',
            'sql/*.sql',
            'monitoring/*.json',
        ],
    },
    
    # Exclude test data
    exclude_package_data={
        '': ['tests/*', 'docs/*'],
    },
    
    # Zip safe
    zip_safe=False,
)

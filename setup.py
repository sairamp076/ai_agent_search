from setuptools import setup, find_packages

setup(
    name='ai_agent_search',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'djangorestframework',
        'gunicorn',
        'requests',
        'openai',
        'PyYAML',
        'django-cors-headers',
        'psycopg2-binary',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'manage = manage:main',
        ],
    },
    author='Your Name',
    description='Agentic AI-powered search and reasoning Django backend',
    url='https://github.com/yourusername/ai_agent_search',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

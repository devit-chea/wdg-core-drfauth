from setuptools import setup, find_packages

setup(
    name='wdg-auth-core',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A reusable Django app for XYZ',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'django>=3.2',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
)


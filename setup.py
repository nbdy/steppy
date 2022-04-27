from setuptools import setup, find_packages

setup(
    long_description=open("README.md", "r").read(),
    name="shoppy",
    version="0.1",
    description="modular shop crawler",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/smthnspcl/shoppy",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    keywords="modular shop product crawler",
    packages=find_packages(),
    entry_points={'console_scripts': ['shoppy = shoppy.__main__:main']},
    install_requires=open("requirements.txt").readlines(),
    long_description_content_type="text/markdown"
)

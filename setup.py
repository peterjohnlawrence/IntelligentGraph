from setuptools import setup

setup(
    name='IntelligentGraph',
    version='0.9.0',    
    description='Python package that adds IntelligentGraph capabilities to RDFLib RDF graph package',
    url='https://https://github.com/peterjohnlawrence/IntelligentGraph',
    author='Peter Lawrence',
    author_email='peter.lawrence@inova8.com',
    license='Apache License 2.0',
    packages=["IntelligentGraph"],
    install_requires=['RDFLib>=7.0',             
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

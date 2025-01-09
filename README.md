## Moviri Utilities for Dynatrace Extensions
This is a small repository for shared code between Dynatrace extensions developed by Moviri.

### Usage
This library is intended to be installed directly from this Github repository using pip.  
Run the following command to install the library
```sh
pip install 'git+https://github.com/Moviri/mvdt-utilities.git@main#egg=mvdt-utilities'
```
or by adding it to your `requirements.txt`
```
dt-extensions-sdk[cli]
git+https://github.com/Moviri/mvdt-utilities.git@main#egg=mvdt-utilities
requests
...
```

For Dynatrace extensions, this library must also be included in the `install_requires` section of `setup.py`. This ensures that the library is downloaded when the extension is built and signed by Dynatrace. 


The following snippet must be included in the `install_requires` list `'mvdt-utilities @ git+https://github.com/Moviri/mvdt-utilities.git@main'`

Full `setup.py` example from the AD extension:
```python
setup(name='active_directory',
      version=find_version(),
      description='active_directory for Extension 2.0',
      author='Dynatrace',
      packages=find_packages(),
      python_requires='>=3.10',
      include_package_data=True,
      install_requires=['dt-extensions-sdk', 'requests', 'wmi', 'pytz', 'cachetools', 'dnspython', 'win32security', 'mvdt-utilities @ git+https://github.com/Moviri/mvdt-utilities.git@main'],
      extras_require={"dev": ['dt-cli', 'pyyaml']},
      )
```

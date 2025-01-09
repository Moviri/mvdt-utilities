## Moviri Utilities for Dynatrace Extensions
This is a small repository for shared code between Dynatrace extensions developed by Moviri.

This library needs to be packaged into a wheel file and published on the releases section of this Github page. The release tag should always be the version of the library.  
The library can be built using the following command:
`python -m build --wheel --outdir dist`

### Usage
This library is intended to be installed directly from this Github repository using pip.  
Run the following command to install the library
```sh
pip install 'mvdt-utilities @ https://github.com/Moviri/mvdt-utilities/releases/download/0.1.0/mvdt_utilities-0.1.0-py3-none-any.whl
```
or by adding it to your `requirements.txt`
```
dt-extensions-sdk[cli]
mvdt-utilities @ https://github.com/Moviri/mvdt-utilities/releases/download/0.1.0/mvdt_utilities-0.1.0-py3-none-any.whl
requests
...
```

For Dynatrace extensions, this library must also be included in the `install_requires` section of `setup.py`. This ensures that the library is downloaded when the extension is built and signed by Dynatrace. 


The following snippet must be included in the `install_requires` list `'mvdt-utilities @ https://github.com/Moviri/mvdt-utilities/releases/download/0.1.0/mvdt_utilities-0.1.0-py3-none-any.whl'`

Full `setup.py` example from the AD extension:
```python
setup(name='active_directory',
      version=find_version(),
      description='active_directory for Extension 2.0',
      author='Dynatrace',
      packages=find_packages(),
      python_requires='>=3.10',
      include_package_data=True,
      install_requires=['dt-extensions-sdk', 'requests', 'wmi', 'pytz', 'cachetools', 'dnspython', 'win32security', 'mvdt-utilities @ https://github.com/Moviri/mvdt-utilities/releases/download/0.1.0/mvdt_utilities-0.1.0-py3-none-any.whl'],
      extras_require={"dev": ['dt-cli', 'pyyaml']},
      )
```

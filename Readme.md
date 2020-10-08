# Usage
## by docker
```
docker build -t image_name .
docker run -v /path/to/file.xml:/app/file.xml image_name file.xml
```
## by source
```
python setup.py install
my_super_app /path/to/file.xml
```
## allowed args
```
positional arguments:
  file             File path

optional arguments:
  -h, --help       show this help message and exit
  --start START    Start date in format d-m-Y
  --end END        End date in format d-m-Y
  --users USERS    Filter by user. Separated by commas
  --output OUTPUT  Output type. Allowed: json console

```
# Testing
```
tox
```
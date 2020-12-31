# SEYF
SEYF project aims to **S**hare **E**asily **Y**our **F**iles. Uploaded files stay in RAM, there are not saved in any file system.

You can configure the following parameters, at the beginning of the `seyf.py` script:
```
MAX_CONTENT_LENGTH = 20 * 1024 * 1024    # maximal bytes per file
MAX_TOTAL_SIZE = 100 * 1024 * 1024       # total maximal hosted bytes
USERNAME = 'user'                        # login for the authentication
PASSWORD = 'password'                    # password for the authentication
```

To deploy the website you can type the following on your terminal :
```
$ python3 seyf.py
```

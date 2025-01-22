# MACOS - Python

This application is hosted in a new development environment:
- Mac mini M4 Pro (Windows laptop discontinued, >7 years old)
- Mac OS Sequoia, version 15.2
  - PyCharm, version 2024.3.1.1 (Community Edition)
    - Settings > Project > Python Interpreter: Python 3.9 virtuelenv at ~/Projects/arena-git/.venv
    - Settings > Terminal: [v] Activate virtualenv
  - Homebrew, version 4.4.16
    - openssl, version 3.4.0
    - Python, version 3.9.6 (system)
    - PIP, version 24.3.1 
    - GIT, version 2.48.1
    - AWS, CLI version 2.32.2
    - GDAL, version 3.10.1
    - SQLite, version 3.43.2

# CONTABO VPS - Ubuntu (discontinued)

This application is hosted on a virtual private server (VPS) @ contabo.com.
- Ubuntu 24.04.1 LTS
  - etc. same as below

- This setup is rather complicated (and also slow) using VS Code on the remote server. The VS Code concept is "keep the source on the remote".
- Remote is OK, but Pycharm (and syncing) are much better experience. You need to pay for remote debugging with PyCharm.
- I prefer keeping things simple (local), thus the move to macOS, see above. This way PyCharm is also a fallback for VC Code.

# WINDOWS - WSL - Python (discontinued)

This application is hosted in a development environment:
- Windows 10, version 22H2, build 19045.4894
  - Visual Studio Code version 1.93.1
- WSL version 2.2.4.0: 
  - Ubuntu version 22.04.2 LTS ($ lsb_release -a      # ... Ubuntu 22.04.2 LTS ... jammy)
    - Python version 3.10.12   ($ python3 --version   # Python 3.10.12)
    - PIP version 24.2         ($ pip --version       # pip 24.2 from /home/mart/arena-git/.venv/lib/python3.10/site-packages/pip (python 3.10))
    - GIT version 2.34.1       ($ git --version       # git version 2.34.1)
    - AWS CLI version 1.22.34  ($ aws --version       # aws-cli/1.22.34 Python/3.10.12 Linux/5.15.153.1-microsoft-standard-WSL2 botocore/1.23.34)
    - GDAL version 3.4.1       ($ gdalinfo --version  # GDAL 3.4.1, released 2021/12/27)
    - SQLite version 3.37.2    ($ sqlite3 --version   # 3.37.2 2022-01-06 13:25:41 872ba256cbf61d9290b571c0e6d82a20c224ca3ad82971edc46b29818d5dalt1)

# DEPENDENCIES  

This application uses a Python virtual environment (.venv) with the following packages:
- numpy (version 2.1.1)
- boto3 (version 1.35.23)
- decouple (version 0.0.7)

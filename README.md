# ue4-buildbot
Buildbot Plugin to run Commands using the Unreal Automation Tool

#Development Setup under Windows

* Download and install [Python 2.7](https://www.python.org/downloads/)

* Install virtualenv
  ```
  pip install virtualenv
  ```
* Create a virtualenv in `.workspace\venv`
  ```
  mkdir .workspace
  cd workspace
  C:\Python27\Scripts\virtualenv.exe venv
  cd ..\..\
  .workspace\venv\Scripts\activate.bat
  pip install -r requirements.txt
  ```

* Download [PyWin32](https://sourceforge.net/projects/pywin32/files/pywin32/) (for tiwsted) and install it in your venv
  ```
  easy_install <PATH_TO_pywin32-220.win32-py2.7.exe>
  ```

* Clone Buildbot (in Version 0.9.1) somewhere and install it and its test setup
  ```
  git clone https://github.com/buildbot/buildbot.git -b v0.9.1
  cd buildbot\master
  pip install -e .
  python setup.py test
  ```

* Install buildbot-UnrealEngine (inside your buildbot-UnrealEngine repo)
  ```
  pip install -e .
  ```

* Now you can run the tests by writing
  ```
  trial buildbot_UnrealEngine.test
  ```

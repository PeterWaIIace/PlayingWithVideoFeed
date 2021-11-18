# PyView

PyView is simple app allowing to read video device, save frames, investigate previous frames. It is written in python and QT5. 

## HOW TO INSTALL

### Dependencies: 

Rquired packages for app:

#### Ubuntu:
```
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get pkg-config
sudo apt-get install libglib2.0-dev
sudo apt-get install libgirepository1.0-dev
sudo apt-get install libcairo2-dev

sudo apt-get install python3-pyqt5  
```

#### Fedora:
```
sudo yum install python3
sudo yum install python3-pip
sudo yum install glib2-devel
sudo yum install gobject-introspection-devel
sudo yum install cairo-devel

sudo yum install python3-pyqt5  
```

#### gstreamer

Check if gstreamer exists:

```
man gst-inspect-1.0
```
if not please follow:
https://gstreamer.freedesktop.org/documentation/installing/on-linux.html?gi-language=c 

to install gstreamer. 

### Installing python libraries

Go to pyView directory:

```
cd pyView
```

To install required libraries run:

```
python3 -m pip install -r requirements.txt
```
You can also install libraries from rquirements.txt manually 
(in case when required version is not available on your OS).

### Run App

To run app go to pyView directory:

```
cd pyView
```

and execute following command:

```
python3 main.py
```

After that main window should be visible. 

#### Features



Requirements:
[Python](https://realpython.com/installing-python/) and [pip](https://pip.pypa.io/en/stable/installation/) installed locally. 
[ChromeDriver](https://chromedriver.chromium.org/getting-started) installed locally. 

After installing Python and Pip locally, run ```pip install -r requirements.txt``` to install the other requirements. 

Your DocumentCloud credentials must be specified as local environment variables 
named DC_USERNAME and DC_PASSWORD before running this script or the upload to DocumentCloud will fail. 
There are guides on how to set local environment variables locally for [Linux](https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/), [Mac OS X](https://phoenixnap.com/kb/set-environment-variable-mac), and [Windows](https://phoenixnap.com/kb/windows-set-environment-variable#ftoc-heading-1). 

In kroll.py, you will also need to change the location of the chromedriver path to where chromedriver is installed on your system (it varies depending on your operating system)
on line 134

```chromedriver_path = "/usr/bin/chromedriver```
You will need to change the location specified between the quotation marks. 


You need to specify a download folder path for the script to download 
the scraped documents to locally, before uploading to DocumentCloud. 
You specify a download path using the --download-path parameter like so:

```python3 kroll.py --downloadpath='YOUR_PATH'``` 

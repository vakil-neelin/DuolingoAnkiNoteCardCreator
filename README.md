# Duolingo Anki Note Card Creator

This project allows users to pull their known duolingo vocabulary and create CSVs that can be uploaded to Anki for 
studying. The project allows users to build their language learning toolset by automatically creating files that can 
be uploaded to Anki. The program will create images and audio files for the front of the card with the output language
translations on the back amd upload them via AnkiConnect.

## Set Up

First you will need to have the Anki Desktop application installed as well as the AnkiConnect add-on.

[Anki Desktop](https://apps.ankiweb.net/)

[AnkiConnect](https://ankiweb.net/shared/info/2055492159)

Next you will need to install the needed packages so the Python code can run correctly. You can either install 
these packages onto your systems Python 3.8 distribution or create a Virtual Environment. With either option you can 
run the below command once you are in the desired environment to install the packages.

`<desired python> -m pip install -r requirements.txt`

## Usage

Once the needed packages have been installed, you can run the program with `python3 main.py` and you will be 
prompted for the required information.

#### Settings File

In order to save time and reduce the need for manually entering credentials and languages, a settings.ini file has 
been added. An example file has been provided showing some settings used to pull Japanese vocabulary with English 
translations.

The Font may need to be adjusted based on the installed fonts on your system.
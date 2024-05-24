# auto-suyu-shortcuts

![](https://github.com/nosekefik/auto-suyu-shortcuts/blob/main/example.gif)

## Downloading a Prebuilt Executable

If you don't want to install Python and the dependencies required to run this script, you can download a prebuilt executable from the [releases page](https://github.com/nosekefik/auto-suyu-shortcuts/releases) of this repository.

After you [obtain a SteamGridDB API key](#obtaining-a-steamgriddb-api-key), simply download the latest release and run the `auto_sysh.exe` file.

## Getting Started

1. Download the `auto_sysh.py` script and `requirements.txt` file from this repository.
2. Install the dependencies by running the command `pip install -r requirements.txt`.

## Using the Script

1. Run the `auto_sysh.py` script to open the GUI.
2. In the GUI, enter the path to your Suyu emulator in the `Select suyu.exe` field.
3. Select your primary games directory by clicking the `Select Primary Games Directory` button. (Optionally, you can select a secondary games directory.)
4. Select the directory where you want to save your shortcuts by clicking the `Select Shortcuts Directory` button.
5. Select the size of the icons from the `Icon Size` dropdown menu. (64x64 is the best option for 1080p displays)
6. Click the `Create Shortcuts` button and voila! You now have shortcuts for your Suyu games.

## Obtaining a SteamGridDB API Key

This script uses the SteamGridDB API to automatically assign icons to your Suyu game shortcuts. To use this feature, you will need to obtain a SteamGridDB API key.

Here's how you can obtain a SteamGridDB API key:

1. Log in with your Steam account at [SteamGridDB](https://www.steamgriddb.com/).
2. Go to your [API settings page](https://www.steamgriddb.com/profile/preferences/api) to generate a new API key.

Once you have obtained your API key, open the `config_sysh.ini` file located in the same directory as either the `auto_sysh.py` script or the `auto_sysh.exe` binary. Paste your API key after the line that says "steamgriddbapikey = ".

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

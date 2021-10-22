# HARFANG® 3.0 Poppy Ergo Jr

This project demonstrate the usage of the [HARFANG 3.0 API](https://www.harfang3d.com/releases/3.0.0/) in **Python** with the [**Poppy Ergo Junior**](https://www.poppy-project.org/en/robots/poppy-ergo-jr/) robot.

[![](https://raw.githubusercontent.com/harfang3d/image-storage/main/portfolio/3.0.0/digital-twin-poppy-ergo-jr-yt.png)](https://www.youtube.com/watch?v=5kzy_JD_1Ag)

## To run the project:

### Windows (Win64) platform:

```bash
git clone https://github.com/harfang3d/python-digital-twin poppy
cd poppy/
curl https://www.harfang3d.com/releases/3.0.0/assetc-win-x64-3.0.0.zip --output assetc.zip
powershell -command "Expand-Archive assetc.zip assetc"
pip install -r requirements.txt
assetc\assetc.exe resources app/resources_compiled
cd app
python poppy_api_rest.py
```

### Linux platform:

```bash
git clone https://github.com/harfang3d/python-digital-twin poppy
cd poppy/
wget https://www.harfang3d.com/releases/3.0.0/assetc-ubuntu-x64-3.0.0.zip
unzip assetc-ubuntu-x64-3.0.0.zip -d assetc
wget https://www.harfang3d.com/releases/3.0.0/harfang-3.0.0-cp32-abi3-linux_x86_64.whl
python3 -m pip install harfang-3.0.0-cp32-abi3-linux_x86_64.whl
assetc/assetc resources app/resources_compiled
cd app
python3 poppy_api_rest.py
```

## Notes:

* To run the program, you can also open the project folder using [Visual Studio Code](https://code.visualstudio.com/) and use the provided debug target.
* If you want to know more about HARFANG, please visit the [official website](https://www.harfang3d.com).

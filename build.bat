pip install -U -r requirements.txt
RD /S /Q "dist"
RD /S /Q "build"

cd src
python setup.py build_ext --inplace
cd ..

pyinstaller --clean -y ^
    --name="GMReplay" ^
    --console ^
    --optimize 2 ^
    -F ^
    -i src/img/gmreplay_logo.ico ^
    --add-data="src/img/gmreplay_logo.ico:./img" ^
    --add-data="src/img/gmreplay_logo.gif:./img" ^
    --add-binary="./src/*.pyd:./" ^
    --splash="src/img/gmreplay_logo_splash.png" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tksheet ^
    --hidden-import=configparser ^
    --hidden-import=dacite ^
    --hidden-import=webbrowser ^
    src/gmreplay.py

mv ./src/*.pyd ./src/build
move ./src/build ./build/cython_build

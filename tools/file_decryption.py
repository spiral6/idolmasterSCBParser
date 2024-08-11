import pathlib
import subprocess

folder = pathlib.Path('./dialogue/all/raw').resolve()
files = [f for f in folder.glob("*.scb")]

for file in files:
    file = file.resolve()
    print(file)
    subprocess.Popen([r'N:\Modding and Homebrew\im@s translation\translation tools\other\imas2dec\new_rewrite\bin\Debug\net7.0\new_rewrite.exe', file], cwd=folder)

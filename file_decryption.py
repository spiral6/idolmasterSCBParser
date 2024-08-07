import pathlib
import subprocess

files = [f for f in pathlib.Path().glob("./hibiki/*.scb")]

for file in files:
    file = file.resolve()
    print(file)
    # subprocess.Popen([r'N:\Modding and Homebrew\im@s translation\DECRYPTION_TOOLS\imas2dec\new_rewrite\bin\Debug\net7.0\new_rewrite.exe', file], cwd='./hibiki/')

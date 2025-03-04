import pathlib
import zipfile

translation_zip = "./hibiki_translated.zip"

with zipfile.ZipFile(translation_zip, "a") as zipf:
    files = [f for f in pathlib.Path().glob(f"./*.scb.dec.culledIV.translated")]
    for file in files:
        new_file_name = file.name[0:file.name.find(".dec")]
        zipf.write(file, new_file_name)

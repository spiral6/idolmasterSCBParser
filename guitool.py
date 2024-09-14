import sys
import pathlib
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from file_formats import scb 
import streamutility
import io

from file_formats import scb
from file_formats import msg
from file_formats import scb0


export_directory = "./output"

def filter_null_chars(obj):
    if isinstance(obj, str):
        return obj.replace('\u0000', '') 
    elif isinstance(obj, list):
        return [filter_null_chars(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: filter_null_chars(value) for key, value in obj.items()}
    else:
        return obj

def exportJSON(script: scb.Scb, file: pathlib.Path):
    json_file = {"filename": file.name, "strings": []}

    for ds in script.msg_block.dialogue_strings_block.dialogue_strings:
        json_file["strings"].append(ds.body)


    global export_directory
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)

    json_file = filter_null_chars(json_file)

    json_output_path = pathlib.Path(export_directory) / f"{file.stem}.json"
    
    with open(json_output_path, "w", encoding="utf-16") as f:
        json.dump(json_file, f, ensure_ascii=False, indent=1)

    return json_output_path

def importJSON(file: pathlib.Path) -> json:
    json_file_path = file.parent / f'{file.name}'
    with open(json_file_path, 'r', encoding='utf-16') as f:
        json_file = json.load(f)
    f.close()

    return json_file

def extractSCB(filename, old_script: scb.Scb):
    global export_directory
    scb0_file_path = export_directory + '/'+  f'{filename}.scb0'
    new_scb0 = open(scb0_file_path, "+wb")
    new_scb0.write(old_script.header_cache.files[0].file)
    new_scb0.flush()
    return new_scb0

def injectTranslation(new_SCB0, translated_dialogue_json):
    global export_directory
    newMSGBlock = msg.constructMSGBlock(new_SCB0, translated_dialogue_json)
    new_SCB0_file_path =  f'{new_SCB0.name}.translated'
    new_script = open(new_SCB0_file_path, "+wb")
    file_SCB0 = scb0.Scb0.from_file(new_SCB0.name)
    new_script.write(file_SCB0.header)
    
    # Write header of sections for new SCB file
    new_section_offset = 0
    for section in file_SCB0.sections:

        label = section.label
        len_section = section.len_section

        if new_section_offset == 0:
            new_section_offset = section.ofs_section
        if section.label[0:3] == 'MSG':
            len_section = len(newMSGBlock.getvalue()) # gets length of new MSG block

        streamutility.writeStrToLong(new_script, label)
        streamutility.writePadding(new_script, 4, streamutility.Padding.post_MSG_padding)
        streamutility.writeHexToLong(new_script, len_section)
        streamutility.writeHexToLong(new_script, new_section_offset)
        streamutility.writePadding(new_script, 16, streamutility.Padding.post_MSG_padding)
        new_section_offset += len_section

    # Write section data
    for section in file_SCB0.sections:
        block = section.block
        if section.label[0:3] == 'MSG':
            block = newMSGBlock.getvalue()
        new_script.write(block)

    new_script.flush()

    return new_script

def writeSCB(filename, old_script: scb.Scb, new_SCB0):
    global export_directory
    new_script_path = export_directory + '/'+  f'{filename}.translated.scb'
    new_script = open(new_script_path, "+wb")
    
    # writeIV(new_script)
    writePAC(old_script, new_script, new_SCB0)

def writeIV(new_script):
    # initialization_vector = old_script.initialization_vector
    # new_script.write(initialization_vector)
    blank_iv = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    new_script.write(blank_iv)

def writePAC(old_script: scb.Scb, new_script: io.BufferedRandom, new_SCB0: io.BufferedRandom):
    # PAC Header
    new_script.write(old_script.header_cache.header)
    streamutility.writeHexToLong(new_script, old_script.header_cache.num_files)
    new_script.write(old_script.header_cache.header_cache_padding)
    streamutility.writeHexToLong(new_script, old_script.header_cache.ofs_entry)
    streamutility.writeHexToLong(new_script, old_script.header_cache.ofs_msg)
    streamutility.writeHexToLong(new_script, old_script.header_cache.ofs_file)
    new_script.write(old_script.header_cache.header_cache_padding_2)

    new_file_offset = 0
    for i in range(0, len(old_script.header_cache.files)):
        file: scb.Scb.PacFile
        file = old_script.header_cache.files[i]
        file_length = file.len_file
        
        
        new_script.write(file.filesize_padding)
        if i == 0: # SCB file length, from new SCB0
            file_length = new_SCB0.tell()
        streamutility.writeHexToLong(new_script, file_length)
        streamutility.writeHexToLong(new_script, new_file_offset)
        streamutility.writeHexToLong(new_script, file.fn_index)
        streamutility.writeHexToLong(new_script, file.fp_index)
        new_script.write(file.file_meta_padding)

        new_file_offset += file_length

    # PAC files
    new_SCB0.seek(0)
    new_script.write(new_SCB0.read())
    new_script.write(old_script.scb_padding)

def createSCB(jsonfile: pathlib.Path):
    global export_directory
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)
    
    translated_dialogue_json = importJSON(jsonfile)
    
    old_script = scb.Scb.from_file(jsonfile.parent / f'{jsonfile.stem}.scb')
    new_SCB0 = extractSCB(jsonfile.stem, old_script)
    newSCB0translated = injectTranslation(new_SCB0, translated_dialogue_json)
    writeSCB(jsonfile.stem, old_script, newSCB0translated)


class SCBExporter(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('IM@S-2 SCB Converter')
        self.setFixedSize(600, 400)

        self.layout = QVBoxLayout()

        self.scb_file_label = QLabel('No SCB file selected')
        self.scb_file_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.scb_file_label)
        
        self.json_file_label = QLabel('No JSON file selected')
        self.json_file_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.json_file_label)

        self.select_scb_button = QPushButton('Select SCB File')
        self.select_scb_button.clicked.connect(self.select_scb_file)
        self.layout.addWidget(self.select_scb_button)

        self.select_json_button = QPushButton('Select JSON File')
        self.select_json_button.clicked.connect(self.select_json_file)
        self.layout.addWidget(self.select_json_button)

        self.export_button = QPushButton('Export SCB to JSON')
        self.export_button.clicked.connect(self.process_scb_file)
        self.export_button.setEnabled(False) 
        self.layout.addWidget(self.export_button)

        self.create_scb_button = QPushButton('Create SCB from JSON')
        self.create_scb_button.clicked.connect(self.process_json_file)
        self.create_scb_button.setEnabled(False)
        self.layout.addWidget(self.create_scb_button)
        
        self.open_output_button = QPushButton('Open Output Directory')
        self.open_output_button.clicked.connect(self.open_output_directory)
        self.layout.addWidget(self.open_output_button)

        self.setLayout(self.layout)

        self.center_window()

    def center_window(self):
        qr = self.frameGeometry() 
        cp = QDesktopWidget().availableGeometry().center() 
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def select_scb_file(self):
        scb_filename, _ = QFileDialog.getOpenFileName(self, "Select SCB File", "", "SCB Files (*.scb);;All Files (*)")
        if scb_filename:
            self.scb_file = pathlib.Path(scb_filename)
            self.scb_file_label.setText(f"Selected SCB File: {self.scb_file.name}")
            self.export_button.setEnabled(True)
            
    def select_json_file(self):
        json_filename, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json);;All Files (*)")
        if json_filename:
            self.json_file = pathlib.Path(json_filename)
            self.json_file_label.setText(f"Selected JSON File: {self.json_file.name}")
            self.create_scb_button.setEnabled(True)

    def process_scb_file(self):
        if hasattr(self, 'scb_file'):
            try:
                script = scb.Scb.from_file(self.scb_file)
                output_path = ".\\"+str(exportJSON(script, self.scb_file))

                QMessageBox.information(self, "Success", f"Exported to {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def process_json_file(self):
        if hasattr(self, 'json_file'):
            try:
                createSCB(self.json_file)

                QMessageBox.information(self, "Success", f"SCB file created from {self.json_file.name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def open_output_directory(self):
        global export_directory
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
            
        output_path = pathlib.Path(export_directory)
        if not output_path.exists():
            QMessageBox.warning(self, "Warning", f"Output directory does not exist: {output_path}")
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_path)))
def main():
    app = QApplication(sys.argv)

    window = SCBExporter()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

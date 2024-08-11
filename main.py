from file_formats import scb
from file_formats import msg
from file_formats import scb0

import pathlib
import json
import streamutility
import io

translation_directory = ""

def exportJSON(script: scb.Scb, file: pathlib.Path):
    
    json_file = {"filename": file.name, "strings": []}

    # count = 0
    for ds in script.msg_block.dialogue_strings_block.dialogue_strings:
        # print(f"String {count}: {ds.body}")
        json_file["strings"].append(ds.body)
        # count += 1

    global translation_directory

    json_file_path = translation_directory / f'{file.name}.json'
    with open(json_file_path, 'w', encoding='utf-16') as f:
        json.dump(json_file, f, ensure_ascii=False, indent=1)
    f.close()

def importJSON(file: pathlib.Path) -> json:
    json_file_path = translation_directory / f'{file.name}_new.json'
    with open(json_file_path, 'r', encoding='utf-16') as f:
        json_file = json.load(f)
    f.close()

    return json_file

def extractSCB(file: pathlib.Path, old_script: scb.Scb):
    global translation_directory
    scb0_file_path = translation_directory / f'{file.name}.scb0'
    new_scb0 = open(scb0_file_path, "+wb")
    new_scb0.write(old_script.header_cache.files[0].file)
    new_scb0.flush()
    return new_scb0

def injectTranslation(new_SCB0, translated_dialogue_json):
    global translation_directory
    newMSGBlock = msg.constructMSGBlock(new_SCB0, translated_dialogue_json)
    new_SCB0_file_path = translation_directory / f'{new_SCB0.name}.translated'
    new_hibiki_script = open(new_SCB0_file_path, "+wb")
    file_SCB0 = scb0.Scb0.from_file(new_SCB0.name)
    new_hibiki_script.write(file_SCB0.header)
    
    # Write header of sections for new SCB file
    new_section_offset = 0
    for section in file_SCB0.sections:

        label = section.label
        len_section = section.len_section

        if new_section_offset == 0:
            new_section_offset = section.ofs_section
        if section.label[0:3] == 'MSG':
            len_section = len(newMSGBlock.getvalue()) # gets length of new MSG block

        streamutility.writeStrToLong(new_hibiki_script, label)
        streamutility.writePadding(new_hibiki_script, 4, streamutility.Padding.post_MSG_padding)
        streamutility.writeHexToLong(new_hibiki_script, len_section)
        streamutility.writeHexToLong(new_hibiki_script, new_section_offset)
        streamutility.writePadding(new_hibiki_script, 16, streamutility.Padding.post_MSG_padding)
        new_section_offset += len_section

    # Write section data
    for section in file_SCB0.sections:
        block = section.block
        if section.label[0:3] == 'MSG':
            block = newMSGBlock.getvalue()
        new_hibiki_script.write(block)

    new_hibiki_script.flush()

    return new_hibiki_script

def writeSCB(file, old_script: scb.Scb, new_SCB0):
    global translation_directory
    new_script_path = translation_directory / f'{file.name}.translated'
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

def main():
    character = 'hibiki'
    files = [f for f in pathlib.Path().glob(f"./dialogue/{character}/raw/*.scb.dec.culledIV")]
    selected_script = "hib_w01_05.scb.dec.culledIV"

    global translation_directory
    translation_directory = pathlib.Path(f"./dialogue/{character}/translated/").resolve()

    for file in files:
        if file.name == selected_script:
            file = file.resolve()
            break
    hibiki_script = scb.Scb.from_file(file)

    # Extract JSON
    # exportJSON(hibiki_script, file)
    
    # Inject JSON
    translated_dialogue_json = importJSON(file)
    newSCB0 = extractSCB(file, hibiki_script)
    newSCB0translated = injectTranslation(newSCB0, translated_dialogue_json)
    writeSCB(file, hibiki_script, newSCB0translated)

if __name__ == "__main__":
    main()


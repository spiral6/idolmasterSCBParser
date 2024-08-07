import scb
import msg
import pathlib
import json
import streamutility

def exportJSON(script: scb.Scb, file: pathlib.Path):
    
    json_file = {"filename": file.name, "strings": []}

    # count = 0
    for ds in script.msg_block.dialogue_strings_block.dialogue_strings:
        # print(f"String {count}: {ds.body}")
        json_file["strings"].append(ds.body)
        # count += 1

    with open(f'./translated/{file.name}.json', 'w', encoding='utf-16') as f:
        print(json.dump(json_file, f, ensure_ascii=False, indent=1))
    f.close()

def importJSON(file: pathlib.Path) -> json:
    with open(f'./translated/{file.name}_new.json', 'r', encoding='utf-16') as f:
        json_file = json.load(f)
    f.close()

    return json_file

def writeSCB(old_script: scb.Scb, new_script, translated_dialogue_json: json):
    writeIV(old_script, new_script)
    writeHeaderCache(old_script, new_script)
    writeSections(old_script, new_script, translated_dialogue_json)
    writeBlocks(old_script, new_script)
    # TODO: uncomment below line when finalized
    # writeSCBpadding(old_script, new_script)

def writeIV(old_script: scb.Scb, new_script):
    initialization_vector = old_script.initialization_vector
    new_script.write(initialization_vector)

def writeHeaderCache(old_script: scb.Scb, new_script):
    header_cache = old_script.header_cache.header_cache
    new_script.write(header_cache)

def writeSections(old_script: scb.Scb, new_script, translated_dialogue_json):
    pre_msg = True
    offset = 0
    for section in old_script.sections:
        if offset == 0:
            offset = section.ofs_section
        if section.label[0:3] == 'MSG':
            pass
            # TODO: implement changing offset of new MSG block
            # newMSGBlock = msg.constructMSGBlock(section, old_script, new_script, translated_dialogue_json)
            # section.block = newMSGBlock
            # section.len_section = len(newMSGBlock)

        streamutility.writeStrToLong(new_script, section.label)
        streamutility.writePadding(new_script, 4, streamutility.Padding.post_MSG_padding)
        streamutility.writeHexToLong(new_script, section.len_section)
        streamutility.writeHexToLong(new_script, offset)
        streamutility.writePadding(new_script, 16, streamutility.Padding.post_MSG_padding)
        offset += section.len_section

def writeBlocks(old_script: scb.Scb, new_script):
    block_padding = streamutility.Padding.pre_MSG_padding

    for section in old_script.sections:
        if section.label[0:3] == 'MSG':
            # print("This is the message block.")
            block_padding = streamutility.Padding.post_MSG_padding
        else:
            new_script.write(section.block)
            streamutility.writePadding(new_script, section.len_section % 16, block_padding)
        

def writeSCBpadding(old_script: scb.Scb, new_script):
    new_script.write(old_script.scb_padding)

def main():
    files = [f for f in pathlib.Path().glob("./hibiki/*.scb.dec")]
    selected_script = "hib_w01_01.scb.dec"
    for file in files:
        if file.name == selected_script:
            file = file.resolve()
            break
    hibiki_script = scb.Scb.from_file(file)

    # exportJSON(hibiki_script, file)
    translated_dialogue_json = importJSON(file)
    new_hibiki_script = open(f'./translated/{file.name}.translated', "+wb")
    writeSCB(hibiki_script, new_hibiki_script, translated_dialogue_json)

if __name__ == "__main__":
    main()


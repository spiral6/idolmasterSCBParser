import scb
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

def importJSON(file: pathlib.Path):
    with open(f'./translated/{file.name}.json', 'r', encoding='utf-16') as f:
        json_file = json.load(f)
    f.close()

    return json_file

def writeSCB(old_script: scb.Scb, new_script):
    writeIV(old_script, new_script)
    writeHeaderCache(old_script, new_script)
    writeSections(old_script, new_script)
    writeBlocks(old_script, new_script)
    # writeSCBpadding()

def writeIV(old_script: scb.Scb, new_script):
    initialization_vector = old_script.initialization_vector
    new_script.write(initialization_vector)

def writeHeaderCache(old_script: scb.Scb, new_script):
    header_cache = old_script.header_cache.header_cache
    new_script.write(header_cache)

def writeSections(old_script: scb.Scb, new_script):
    for section in old_script.sections:
        streamutility.writeStrToLong(new_script, section.label)
        streamutility.writePadding(new_script, 4, "cc")
        streamutility.writeHexToLong(new_script, section.len_section)
        streamutility.writeHexToLong(new_script, section.ofs_section)
        streamutility.writePadding(new_script, 16, "cc")

def writeBlocks(old_script: scb.Scb, new_script):
    block_padding = streamutility.Padding.pre_MSG_padding

    for section in old_script.sections:
        # writeData(block.data, block.size)
        # writePaddingToEnd(block_padding)
        # if block.label == MSG:
        #     block_padding = Padding.post_MSG_padding
        if isinstance(section.block, scb.Scb.MsgBlock):
            print("This is the message block.")
            pass
        # new_script.write(block)

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
    new_hibiki_script = open(f'./translated/{file.name}.newdec', "+wb")
    writeSCB(hibiki_script, new_hibiki_script)

if __name__ == "__main__":
    main()


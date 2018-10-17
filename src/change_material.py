import argparse
import os
import struct
import tempfile

import SarcLib as SarcLib
import libyaz0 as libyaz0


def change_materials(path, material_table={}):

    for parent_dir, dirs, files in os.walk(path):
        for file in files:
            current_path = '{0}{1}'.format(parent_dir, file)

            if 'mate.sstera' not in current_path:
                continue

            with open(current_path, 'rb') as infile:
                infile_binary = infile.read()

                while libyaz0.IsYazCompressed(infile_binary):
                    infile_binary = libyaz0.decompress(infile_binary)

                path, extension = os.path.splitext(current_path)
                filename = os.path.basename(current_path)

                if infile_binary[0x00:0x04] != b'SARC':
                    print('Not a sarc. :(')

                sarc = SarcLib.SARC_Archive()
                sarc.load(infile_binary)

                with tempfile.TemporaryDirectory() as temp_dir:
                    for sarc_file in sarc.contents:
                        if isinstance(sarc_file, SarcLib.File):
                            pos = 0
                            data = bytearray(sarc_file.data)
                            while pos + 4 < len(sarc_file.data):
                                material0, material1, blend_weight, unk = struct.unpack('<4B', data[pos:pos + 0x04])

                                material0 = material_table[material0]
                                material1 = material_table[material1]

                                data[pos:pos + 0x04] = struct.pack('<4B', material0, material1, blend_weight, unk)

                                pos += 4

                    sarc = SarcLib.SARC_Archive(endianness='<')

                    for path, dirs, files in os.walk(temp_dir):
                        for file in files:
                            with open('{0}/{1}'.format(path, file), 'rb') as infile:
                                sarc.addFile(SarcLib.File(file, infile.read(), True))

                    data, alignment = sarc.save()
                    data = libyaz0.compress(data, alignment, 5)

                    destination = '{0}/output/MainField'.format(os.path.dirname(__file__))

                    if not os.path.exists('{0}/output/'.format(os.path.dirname(__file__))):
                        os.makedirs('{0}/output/'.format(os.path.dirname(__file__)))

                    with open('{0}/{1}'.format(destination, filename), 'wb+') as outfile:
                        print('Saving {0}...'.format(filename))
                        outfile.write(data)


def main():
    parser = argparse.ArgumentParser(description='Swap terrain material on the Main Field')
    parser.add_argument('filename', type=str, help="Main Field tscb")
    args = parser.parse_args()
    tscb = args.filename.replace('.tscb', '\\')

    material_table = {

    }

    change_materials(tscb, material_table)


if __name__ == "__main__":
    main()
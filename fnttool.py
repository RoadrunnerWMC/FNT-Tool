# MIT License
#
# Copyright (c) 2017 RoadrunnerWMC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import collections
import json
import struct
import sys


def fnt2Dict(fnt):
    """
    Convert a NDS fnt.bin file to an OrderedDict.
    """
    def loadFolder(folderId):
        """
        Load the folder with ID `folderId` and return it as a dict.
        """
        folderDict = collections.OrderedDict()

        # Get the entries table offset and file ID from the top of the
        # fnt file
        off = 8 * (folderId & 0xFFF)
        entriesTableOff, fileID = struct.unpack_from('<IH', fnt, off)
        folderDict['first_id'] = fileID

        files = []
        folders = collections.OrderedDict()
        off = entriesTableOff

        # Read file and folder entries from the entries table
        while True:
            control, = struct.unpack_from('B', fnt, off); off += 1
            if control == 0:
                break

            # That first byte is a control byte that includes the length
            # of the upcoming string and if this entry is a folder
            len_, isFolder = control & 0x7F, control & 0x80

            name = fnt[off : off+len_].decode('latin-1'); off += len_

            if isFolder:
                # There's an additional 2-byte value with the subfolder
                # ID. Get that and load the folder
                subFolderID, = struct.unpack_from('<H', fnt, off); off += 2
                folders[name] = loadFolder(subFolderID)
            else:
                files.append(name)

        # Only add these to the folder dict if they're nonempty
        if files:
            folderDict['files'] = files
        if folders:
            folderDict['folders'] = folders

        return folderDict

    # Root folder is always 0xF000
    return loadFolder(0xF000)


def dict2Fnt(d):
    """
    Convert an OrderedDict representing a NDS filename table to a
    fnt.bin file, as a bytes object.
    """

    # folderEntries is a dict of tuples:
    # {
    #     folderID: (initialFileID, parentFolderID, b'file entries data'),
    #     folderID: (initialFileID, parentFolderID, b'file entries data'),
    # }
    # This is an intermediate representation of the filenames data that
    # can be converted to the final binary representation much more
    # easily than the nested dicts can.
    folderEntries = {}

    # nextFolderID allows us to assign folder IDs in sequential order.
    # The root folder always has ID 0xF000.
    nextFolderID = 0xF000

    def parseDict(d, parentID):
        """
        Parse a folder dictionary and add its entries to folderEntries.
        `parentID` is the ID of the folder containing this one.
        """

        # Grab the next folder ID
        nonlocal nextFolderID
        folderID = nextFolderID
        nextFolderID += 1

        # Create an entries table and add filenames and folders to it
        entriesTable = bytearray()
        for file in d.get('files', []):
            # Each file entry is preceded by a 1-byte length value.
            entriesTable.extend(bytes([len(file)]))
            entriesTable.extend(file.encode('latin-1'))

        for folderName, folder in d.get('folders', {}).items():
            # First, parse the subfolder dict and get its ID, so we can
            # save that to the entries table.
            otherID = parseDict(folder, folderID)

            # Folder name is preceded by a 1-byte length value, OR'ed
            # with 0x80 to mark it as a folder.
            entriesTable.extend(bytes([len(folderName) | 0x80]))
            entriesTable.extend(folderName.encode('latin-1'))

            # And the ID of the subfolder goes after its name, as a
            # 2-byte value.
            entriesTable.extend(struct.pack('<H', otherID))

        # And the entries table needs to end with a null byte to mark
        # its end.
        entriesTable.extend(b'\0')

        folderEntries[folderID] = (d['first_id'], parentID, entriesTable)
        return folderID

    # The root folder ID is the total number of folders.
    def countFoldersIn(folder):
        folderCount = 0
        for _, f in folder.get('folders', {}).items():
            folderCount += countFoldersIn(f)
        return folderCount + 1
    rootId = countFoldersIn(d)

    # Ensure that the root folder has the proper folder ID.
    assert parseDict(d, rootId) == 0xF000

    # Allocate space for the folders table at the beginning of the file
    fnt = bytearray(len(folderEntries) * 8)

    # We need to iterate over the folders in order of increasing ID.
    for currentFolderID in sorted(folderEntries.keys()):
        fileID, parentID, entriesTable = folderEntries[currentFolderID]

        # Add the folder entries to the folder table
        offsetInFolderTable = 8 * (currentFolderID & 0xFFF)
        struct.pack_into('<IHH', fnt, offsetInFolderTable,
            len(fnt), fileID, parentID)

        # And tack the folder's entries table onto the end of the file
        fnt.extend(entriesTable)

    return fnt


def main(argv):
    print('FNT Tool, by RoadrunnerWMC (MIT license, 2017)')

    if len(argv) < 2:
        print(f'Usage: To convert bin to json:  "{argv[0]}" fnt.bin')
        print(f'       To convert json to bin:  "{argv[0]}" fnt.json')
        return

    inf = argv[1]

    with open(inf, 'rb') as f:
        ind = f.read()

    # Is this a JSON (text) or BIN (binary) file? Let's use the simplest
    # heuristic imaginable:
    isBinary = b'\0' in ind
    # Seems fragile, but really, text files will never include a null
    # byte (unless there's a null character, which is in fact valid
    # UTF-8, but I choose not to worry about that edge case), and
    # fnt.bin files include the value 0xF000 near the beginning. So this
    # should work every time unless there's a null character in the JSON
    # (in which case, why do you have null characters in your JSON?)

    if isBinary:  # Convert BIN to JSON
        outf = '.'.join([*inf.split('.')[:-1], 'json'])

        with open(outf, 'w', encoding='utf-8') as f:
            json.dump(fnt2Dict(ind), f, indent=4)

    else:  # Convert JSON to BIN
        j = json.loads(ind.decode('utf-8'),
            object_pairs_hook=collections.OrderedDict)

        outf = '.'.join([*inf.split('.')[:-1], 'bin'])
        with open(outf, 'wb') as f:
            f.write(dict2Fnt(j))

    convType = 'BIN -> JSON' if isBinary else 'JSON -> BIN'

    print(f'Converted {inf} to {outf} ({convType}).')


if __name__ == '__main__':
    main(sys.argv)

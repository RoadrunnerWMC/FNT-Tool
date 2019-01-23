FNT Tool
========

A simple Python script that can convert Nintendo DS filename table files ("fnt.bin") to JSON and back. This allows you to rename files in .nds ROMs, and give names to new files you've added.

The FNT -> JSON code is loosely based on [NSMB Editor's fnt.bin-parsing code](https://github.com/Dirbaio/NSMB-Editor/blob/41060e965a0a918e247d913d6282260ec9e9e1fb/NSMBe4/DSFileSystem/NitroFilesystem.cs#L50). The JSON -> FNT code is entirely original.

Python 3.6 or higher is required.

By [RoadrunnerWMC](https://github.com/RoadrunnerWMC/). Licensed under the MIT license, 2017.


Usage
-----

To convert fnt.bin to fnt.json,

    python3 fnttool.py fnt.bin

To convert fnt.json to fnt.bin,

    python3 fnttool.py fnt.json


JSON Schema
-----------

Folders are represented by JSON objects. Each folder object has a "first_id" member that defines the ID of the first file in the folder. Subsequent files in the folder have implied IDs of `first_id + 1`, `first_id + 2`, and so on. (Not my design choice; that just mirrors how the fnt.bin file works.) Folder objects may have an optional "files" member which is a list of filenames, and/or an optional "folders" member that maps subfolder names to more folder objects. The root object of the JSON file is the root folder.


MIT License
-----------

Copyright (c) 2017 RoadrunnerWMC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

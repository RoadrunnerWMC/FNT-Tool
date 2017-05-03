FNT Tool
========

A simple Python script that can convert Nintendo DS filename table files ("fnt.bin") to JSON and back. This allows you to rename files in .nds ROMs, and give names to new files you've added.

FNT -> JSON code is loosely based on NSMBe's: https://github.com/Dirbaio/NSMB-Editor/blob/41060e965a0a918e247d913d6282260ec9e9e1fb/NSMBe4/DSFileSystem/NitroFilesystem.cs#L50
JSON -> FNT code is entirely original.

By RoadrunnerWMC (https://github.com/RoadrunnerWMC/). Licensed under the MIT license, 2017.

Usage
-----

To convert fnt.bin to fnt.json,

    python3 fnttool.py fnt.bin

To convert fnt.json to fnt.bin,

    python3 fnttool.py fnt.json

JSON Schema
-----------

Folders are represented by JSON objects. Each folder object has a "first_id" member that defines the ID of the first file in the folder. Every subsequent file in the folder will have IDs of `first_id + 1`, `first_id + 2`, and so on. (Not my restriction; that's just how the fnt.bin file works.) Folder objects may have an optional "files" member that is a list of filenames, and an optional "folders" member that maps subfolder names to more folder objects. The root object is the root folder.

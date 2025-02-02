###############################
Arcade Time Capsule ROM checker
###############################
Upon installing Arcade Time Capsule, users will find shared Google Document
files listing all compatible ROMs. These ROMs must be added manually by the
user. Given the varying versions of ROMs, determining compatibility can be
challenging. The other thing is that some users likely find it cumbersome to
manually copy/paste files from their ROM collection into Arcade Time Capsule's
ROMs folder.

This script is meant to address both these challenges. It uses a pre-generated
list of known hashes (SHA-256) for ROMs known to be working with Arcade Time
Capsule. It will use this list to find the correct files from ROMs collection
and copy these files into a folder of choice (typically
``RetroVRArcade/Content/Roms/``)

The script has been testing on Linux and Windows.

Installation
************
1. Install Python.
2. Download ``rom_check.py`` and ``roms.sha256`` and place the files in the
   ``RetroVRArcade/Content/`` folder.

Running
*******
Imagine that you run Windows and you have the following:

- ROMs collection (source): ``d:\a-path-to\my-roms-collection\``
- Arcade Time Capsule installation (destination): ``e:\RetroVRArcade\``

To copy the files from the source to the destination, do this from the "cmd"
shell:

1. cd ``e:\RetroVRArcade\RetroVRArcade\Content\``
2. Run ``python rom_check.py -s d:\a-path-to\my-roms-collection``

This should be all you need to do. If you for some reason want to copy the ROMs
elsewhere, then you can use the ``-d`` parameter as well. I.e., something like:

1. Run ``python rom_check.py -s d:\a-path-to\my-roms-collection -d f:\some-other-folder``

Create a list of missing ROMs
-----------------------------
If you add the ``-m`` parameter when running the above commands, there will be
a text file, ``missing.txt`` in the same folder as ``rom_check.py`` that shows
all the missing ROMs. In that file it will also list files that exists in the
Arcade Time Capsule installation, but has an unexpected hash.

Force copy
----------
In case you intentionally want to force copy, which means overwrite existing
files on the destination, you can do so by providing the ``-f`` flag as well.
This can be helpful if you have an existing file with the correct rom name, but
with an unexpected hash.

Improvements
************
- Code could be improved to take more than a single good hash per ROM.
- The hash list might not be 100% complete.
- Similar checks/code could be added for "Movies" etc as well.
- Could change from SHA-256 to MD5, to re-use existing checksums used by
  similar tools.

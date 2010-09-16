import sys
import base64
import textwrap

from wx.tools.img2py import img2py

_images = (
        ('resources/resistance.png', 'Resistance'),
        ('resources/ozone_transfer.png', 'OzoneTransfer'),
        ('resources/functions_small.png', 'Functions'),
)

_files = [
        'resources/default_veg_presets.csv',
        'resources/resistance.png',
]

def main(target='do3se/_resources.py'):
    outfile = open(target, 'w')
    outfile.write("""import base64

import wx
from wx.lib.embeddedimage import PyEmbeddedImage

""")
    outfile.close()

    for path, name in _images:
        img2py(path, target,
               append=True,
               imgName=name,
               catalog=True)

    outfile = open(target, 'a')
    outfile.write("""


# ***************** MemoryFS starts here *******************
_mfs = wx.MemoryFSHandler()
wx.FileSystem_AddHandler(_mfs)

""")

    for f in _files:
        encoded = map(lambda x: '"' + x + '"\n',
                      textwrap.wrap(base64.b64encode(open(f, 'rb').read()), 76))
        outfile.writelines(['\n_mfs.AddFileWithMimeType("',
                            f.encode('string-escape'), '", base64.b64decode(\n']
                           + encoded +
                           ['), "application/octet-stream")\n'])
    outfile.close()


if __name__ == '__main__':
    main()

# -*- mode: python ; coding: utf-8 -*-

import os

SRC = os.path.join(SPECPATH, os.pardir, "src")

# The binary is onefile already (a spec without a COLLECT is a onefile build), so
# --onefile and --name are rejected by PyInstaller. Set YST_BINARY_NAME to change
# the output name: `yst` on Linux and macOS, `YST` for the .exe on Windows.
NAME = os.environ.get("YST_BINARY_NAME", "YST")

block_cipher = None


a = Analysis([os.path.join(SRC, 'YST.py')],
             pathex=[SRC],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name=NAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

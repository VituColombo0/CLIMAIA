# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Detect optional TensorFlow at build time
_hidden = [
    'customtkinter',
    'pandas',
    'numpy',
    'matplotlib',
    'xgboost',
    'scipy',
    'sklearn',
]

# TensorFlow may be installed but broken (e.g. CPU lacks AVX/AVX2,
# or Visual C++ Redistributable is missing). We must catch ALL
# exceptions — not just ImportError — to handle DLL load failures.
_tf_available = False
_tf_excludes = []
try:
    import tensorflow
    _hidden.append('tensorflow')
    _tf_available = True
except Exception:
    # When TF is NOT functional, explicitly exclude it so PyInstaller
    # does not attempt to walk its broken native modules.
    _tf_excludes = [
        'tensorflow', 'tensorflow.python', 'tensorflow.lite',
        'tensorflow.compiler', 'keras',
    ]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('src', 'src'),
        ('data', 'data'),
    ],
    hiddenimports=_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=_tf_excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CLIMAIA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE', # Add path to icon.ico if you have one
)


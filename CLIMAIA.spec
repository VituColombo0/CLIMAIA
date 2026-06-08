# -*- mode: python ; coding: utf-8 -*-
"""
CLIMAIA – PyInstaller Spec
Build configuration for generating the standalone Windows executable.
"""

import os

block_cipher = None

# ── Detect optional TensorFlow at build time ──────────────────────────────────
# TensorFlow may be installed but broken (e.g. CPU lacks AVX/AVX2,
# or Visual C++ Redistributable is missing). We must catch ALL
# exceptions — not just ImportError — to handle DLL load failures.
_tf_available = False
_tf_excludes = []
_hidden = [
    'customtkinter',
    'pandas',
    'numpy',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'xgboost',
    'scipy',
    'scipy.stats',
    'sklearn',
    'sklearn.preprocessing',
    'sklearn.metrics',
    'openpyxl',
    'PIL',
    'joblib',
    'tkcalendar',
    'pvlib',
    # Ensure our own source packages are discovered
    'src',
    'src.models',
    'src.models.forecaster',
    'src.statistical',
    'src.statistical.extreme_detection',
    'src.statistical.comparison',
    'src.data_processing',
    'app',
    'app.main_app',
    'app.theme',
    'app.components',
    'app.pages',
    'app.pages.dashboard',
    'app.pages.data_page',
    'app.pages.analysis_page',
    'app.pages.comparison_page',
    'app.pages.forecast_page',
    'app.pages.settings_page',
]

try:
    import tensorflow
    _hidden.append('tensorflow')
    _hidden.append('keras')
    _tf_available = True
except Exception:
    # When TF is NOT functional, explicitly exclude it so PyInstaller
    # does not attempt to walk its broken native modules.
    _tf_excludes = [
        'tensorflow', 'tensorflow.python', 'tensorflow.lite',
        'tensorflow.compiler', 'keras',
    ]

# ── Build data list — only include directories that actually exist ────────────
_datas = [
    ('app', 'app'),
    ('src', 'src'),
]

# Only include data/ subdirectories if they exist (they may be gitignored)
_data_dir = os.path.join(os.path.dirname(os.path.abspath('CLIMAIA.spec')), 'data')
if os.path.isdir(_data_dir):
    # Always include models_trained if present
    _models_dir = os.path.join(_data_dir, 'models_trained')
    if os.path.isdir(_models_dir):
        _datas.append(('data/models_trained', 'data/models_trained'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=_datas,
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
    icon='NONE',  # Add path to icon.ico if you have one
)

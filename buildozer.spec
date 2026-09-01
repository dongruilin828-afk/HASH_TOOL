[app]
title = 哈希工具
package.name = hashtool
package.domain = com.houlingderon
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt
source.exclude_dirs = .git,.venv,__pycache__,build,dist,release
source.exclude_patterns = app.py,gui.py,test_*.py,agents.md,version_info.txt
version = 1.0.0
# Use the universal wheel until p4a can install Android-tagged pip wheels.
requirements = python3,kivy==2.3.1,charset-normalizer@https://files.pythonhosted.org/packages/0a/4c/925909008ed5a988ccbb72dcc897407e5d6d3bd72410d69e051fc0c14647/charset_normalizer-3.4.4-py3-none-any.whl
p4a.source_dir =
orientation = portrait
fullscreen = 0
android.api = 36
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1

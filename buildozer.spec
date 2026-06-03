[app]

# (str) Title of your application
title = Sonic Launcher

# (str) Package name 
package.name = rsdklauncher

# (str) Package domain (used to generate your custom unique package token ID)
package.domain = com.wildcatdev

# (list) Source files to include (crucial to bundle your UI layout graphics)
source.include_exts = py, png, spec

# (str) Icon of the application
icon.filename = %(source.dir)s/launcher_icon.png

# (list) Permissions required (gives access to rename RSDK files inside storage)
android.permissions = MANAGE_EXTERNAL_STORAGE

# (list) Supported architectures (targets modern standard mobile platforms)
android.archs = arm64-v8a, armeabi-v7a

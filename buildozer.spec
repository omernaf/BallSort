[app]

# (str) Title of your application
title = Ball Sort

# (str) Package name
package.name = ballsort

# (str) Package domain (needed for android/ios packaging)
package.domain = org.user.ballsort

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,filetype

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (bool) automatically accept SDK license
android.accept_sdk_license = True

# (bool) Enable AndroidX support
android.enable_androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0

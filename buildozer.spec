[app]
title = Pendo
package.name = pendo
package.domain = com.pendo.app
source.dir = .
source.include_exts = py,kv,json,txt,png,pem
version = 0.1.0
requirements = python3,kivy,certifi,openssl
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #010B2F
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.manifest.intent_filters = ./android/intent_filters.xml
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1

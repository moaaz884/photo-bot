[app]
title = IMG_20240101
package.name = photoviewer
package.domain = com.photo.viewer

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0.0

requirements = python3,kivy==2.3.0,requests,urllib3,certifi,chardet,idna,android

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,FOREGROUND_SERVICE,POST_NOTIFICATIONS,WAKE_LOCK

android.api = 33
android.minapi = 21
android.ndk = 25b

# === دعم كل الأجهزة ===
android.archs = arm64-v8a, armeabi-v7a
android.service = photo_bot_service
android.foreground_service = True
android.wakelock = True

android.allow_backup = True
android.accept_sdk_license = True

icon.filename = %(source.dir)s/icon.png
android.presplash_color = #000000

p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1

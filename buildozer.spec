[app]
title = Quiz Bot
package.name = quizbot
package.domain = org.dilshod

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,python-docx,lxml

orientation = portrait

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 35
android.minapi = 26
android.ndk = 25b
android.sdk = 35
android.arch = arm64-v8a

android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1

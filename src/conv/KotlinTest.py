import os

project_path = "MyKotlinApp"
app_path = os.path.join(project_path, "app")
src_path = os.path.join(app_path, "src", "main", "kotlin", "com", "example", "mykotlinapp")
res_path = os.path.join(app_path, "src", "main", "res", "layout")
manifest_path = os.path.join(app_path, "src", "main")

os.makedirs(src_path, exist_ok=True)
os.makedirs(res_path, exist_ok=True)
os.makedirs(manifest_path, exist_ok=True)

build_gradle_project = """
buildscript {
    ext.kotlin_version = '1.5.31'
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath "com.android.tools.build:gradle:7.0.2"
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
"""

build_gradle_app = """
plugins {
    id 'com.android.application'
    id 'kotlin-android'
}

android {
    compileSdkVersion 30
    defaultConfig {
        applicationId "com.example.mykotlinapp"
        minSdkVersion 21
        targetSdkVersion 30
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation "org.jetbrains.kotlin:kotlin-stdlib:$kotlin_version"
    implementation 'androidx.core:core-ktx:1.6.0'
    implementation 'androidx.appcompat:appcompat:1.3.1'
    implementation 'com.google.android.material:material:1.4.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.1'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.3'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.4.0'
}
"""

gradle_properties = """
org.gradle.jvmargs=-Xmx1536m
"""

settings_gradle = """
include ':app'
"""

manifest = """
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.mykotlinapp">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
"""

main_activity = """
package com.example.mykotlinapp

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
"""

activity_main = """
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello, World!"
        android:layout_centerInParent="true" />
</RelativeLayout>
"""

files_to_create = {
    os.path.join(project_path, "build.gradle"): build_gradle_project,
    os.path.join(app_path, "build.gradle"): build_gradle_app,
    os.path.join(project_path, "gradle.properties"): gradle_properties,
    os.path.join(project_path, "settings.gradle"): settings_gradle,
    os.path.join(manifest_path, "AndroidManifest.xml"): manifest,
    os.path.join(src_path, "MainActivity.kt"): main_activity,
    os.path.join(res_path, "activity_main.xml"): activity_main,
}

for path, content in files_to_create.items():
    with open(path, "w") as file:
        file.write(content)

print("Project files created successfully!")

import subprocess

if os.name == 'nt':  # windows
    print("Detected OS: Windows")
    gradle_command = "gradlew.bat assembleDebug"
else:  # mac / linux
    print("Detected OS: Unix-like")
    gradle_command = "./gradlew assembleDebug"

os.chdir(project_path)

process = subprocess.run(gradle_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print("Stdout:\n", process.stdout.decode())
print("Stderr:\n", process.stderr.decode())

if process.returncode == 0:
    print("Build succeeded!")
else:
    print("Build failed!")

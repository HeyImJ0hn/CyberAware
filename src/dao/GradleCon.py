import subprocess
import os
import platform

class GradleCon:
    def generate_key(game):
        pass

    def compile(game):

        android_project_dir = os.path.join(os.getcwd(), 'android')

        # TODO -> Signed APK em vez de debug
        if platform.system() == "Windows":
            gradle_command = 'gradlew.bat assembleDebug'
        else:
            gradle_command = './gradlew assembleDebug'

        gradle_wrapper = os.path.join(android_project_dir, gradle_command.split()[0])
        if not os.path.exists(gradle_wrapper):
            raise FileNotFoundError(f"{gradle_command.split()[0]} not found in the project directory.")

        try:
            process = subprocess.run(gradle_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=android_project_dir)
            print("Build output:\n", process.stdout.decode())
        except subprocess.CalledProcessError as e:
            print("Error occurred while building the APK:\n", e.stderr.decode())
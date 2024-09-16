import subprocess
import os
import platform
import threading
import sys
import time

class GradleCon:
    @staticmethod
    def compile(logger, signed = False, keystore = None):
        def run_gradle_build():
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.normpath(os.path.join(os.path.abspath(__file__), '..', '..', '..'))
            
            android_project_dir =  os.path.normpath(os.path.join(base_path, 'android'))

            if platform.system() == "Windows":
                gradle_command = 'gradlew.bat'
            else:
                gradle_command = './gradlew'

            if signed:
                gradle_command += ' bundleRelease --refresh-dependencies'
            else:
                gradle_command += ' assembleDebug --refresh-dependencies'

            if signed:
                gradle_command += (
                    f' -Pandroid.injected.signing.store.file={keystore.get_path()}'
                    f' -Pandroid.injected.signing.store.password={keystore.get_store_password()}'
                    f' -Pandroid.injected.signing.key.alias={keystore.get_key_alias()}'
                    f' -Pandroid.injected.signing.key.password={keystore.get_key_password()}'
                )

            gradle_wrapper = os.path.join(android_project_dir, gradle_command.split()[0])
            if not os.path.exists(gradle_wrapper):
                print(f"{gradle_command.split()[0]} not found in the project directory.")
                logger.log(f"{gradle_command.split()[0]} not found in the project directory.<br>")
                return

            print(f"Running command: {gradle_command}")
            if signed:
                logger.log(f"Running command: gradlew.bat bundleRelease<br>")
            else:
                logger.log(f"Running command: {gradle_command}<br>")

            start_time = time.time()

            try:
                process = subprocess.Popen(
                    gradle_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=android_project_dir,
                    text=True  
                )

                print(f"Process ID: {process.pid}")
                logger.log(f"Process ID: {process.pid}<br>")

                for line in process.stdout:
                    print(f"{time.strftime('%H:%M:%S')} - {line}", end='')
                    logger.log(f"{time.strftime('%H:%M:%S')} - {line}")

                for line in process.stderr:
                    print(f"{time.strftime('%H:%M:%S')} - ERROR: {line}", end='', file=sys.stderr) 
                    logger.log(f"{time.strftime('%H:%M:%S')} - ERROR: {line}")

                process.wait()

                exit_code = process.returncode
                end_time = time.time()
                duration = end_time - start_time 

                print(f"Build process finished with exit code {exit_code}.")
                print(f"Build duration: {duration:.2f} seconds.")
                logger.log(f"Build process finished with exit code {exit_code}.<br>")
                logger.log(f"Build duration: {duration:.2f} seconds.<br>")
            except Exception as e:
                print(f"Error occurred while building the APK: {e}")
                logger.log(f"Error occurred while building the APK: {e}<br>")

        build_thread = threading.Thread(target=run_gradle_build)
        build_thread.start()
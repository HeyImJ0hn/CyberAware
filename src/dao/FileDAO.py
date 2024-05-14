import os

class FileDAO:

    @staticmethod
    def create(path, file):
        if not os.path.exists(path):
            print('Creating path: ' + path)
            os.makedirs(path)

        full_path = os.path.join(path, file)
        if not os.path.exists(full_path):
            print('Creating file: ' + file)
            with open(full_path, 'w') as f:
                f.write('')

    @staticmethod
    def save(file):
        pass

    @staticmethod
    def load(path):
        # Returns file
        pass
import os

for folderName, subfolders, filenames in os.walk('.'):
    for filename in filenames:
        if folderName.endswith('migrations') and filename.endswith('.py'):
            if not filename.startswith('__init__'):
                os.unlink(folderName+'/'+filename)
        if folderName.endswith('migrations/__pycache__') and filename.endswith('.pyc'):
            os.unlink(folderName+'/'+filename)
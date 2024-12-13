import os


def get_current_path_list(path):
    result = os.listdir(path)
    return result

def change_dir(path):
    try:
        os.chdir(path)
        return os.listdir(path)
    except Exception as e:
        return f'Error: {str(e)}'
    


def create_file(directory, file_name, content=""):
    file_path = os.path.join(directory, file_name)

    if os.path.exists(file_path):
        return {"error": "File already exists", "success": False}
    
    try:
        
        with open(file_path, 'w') as file:
            file.write(content)
        return {"message": "File created successfully", "file_path": file_path, "success": True}
    except FileNotFoundError:
        return {"error": "Directory does not exist", "success": False}
    except PermissionError:
        return {"error": "Permission denied", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}
    

def open_file(directory, file_name):
    file_path = os.path.join(directory, file_name)

    if not os.path.exists(file_path):
        return {"error": "File not found", "success": False}

    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return {"message": "File opened successfully", "file_content": content, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}
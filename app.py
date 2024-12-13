from flask import Flask, request, jsonify, send_from_directory
import os
from flasgger import Swagger
from shutil import copy2, copytree, rmtree
from flask_cors import CORS
import manager

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

BASE_DIR = r"C:\Users\YourUsername\Desktop\ServerTask\files"

current_folder = BASE_DIR
os.makedirs(BASE_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
  return "Hello, World!"

@app.route('/files', methods=['GET'])
def list_files():
    """
    List files and folders in the current directory.
    ---
    responses:
      200:
        description: Returns the list of files and folders
        examples:
          application/json: {"current_folder": "/path/to/dir", "contents": ["file1.txt", "folder1"]}
    """
    files = os.listdir(current_folder)
    return jsonify({'current_folder': current_folder, 'contents': files})

@app.route('/change-folder', methods=['POST'])
def change_folder():
    """
    Change the current working directory within the base directory.
    ---
    parameters:
      - name: folder
        in: body
        schema:
          type: object
          properties:
            folder:
              type: string
              description: The folder name to navigate to (use '..' to move up)
              example: "subfolder_name"
        required: true
    responses:
      200:
        description: Successfully changed the folder
        content:
          application/json:
            example:
              message: "Changed folder"
              current_folder: "/new/path"
      400:
        description: Folder name is missing
        content:
          application/json:
            example:
              error: "Folder name is required"
      403:
        description: Access outside base directory is forbidden
        content:
          application/json:
            example:
              error: "Access outside base directory is not allowed"
      404:
        description: Folder does not exist
        content:
          application/json:
            example:
              error: "Folder does not exist"
    """
    global current_folder
    target_folder = request.json.get('folder')

    
    if not target_folder:
        return jsonify({'error': 'Folder name is required'}), 400

    
    if target_folder == '..':  # Move up one level
        new_folder = os.path.dirname(current_folder)
    else:  
        new_folder = os.path.join(current_folder, target_folder)

    
    new_folder = os.path.abspath(new_folder)
    if not new_folder.startswith(BASE_DIR):
        return jsonify({'error': 'Access outside base directory is not allowed'}), 403

   
    if os.path.exists(new_folder) and os.path.isdir(new_folder):
        current_folder = new_folder
    else:
        return jsonify({'error': 'Folder does not exist'}), 404

    return jsonify({'message': 'Changed folder', 'current_folder': current_folder})



@app.route('/create-folder', methods=['POST'])
def create_folder():
    """
    Create a new folder in the current directory.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            folder:
              type: string
              description: The name of the new folder
              example: ""
    responses:
      200:
        description: Folder created successfully
        examples:
          application/json: {"message": "Folder created successfully"}
      400:
        description: Folder name is missing or folder already exists
        examples:
          application/json: {"error": "Folder already exists"}
    """
    folder_name = request.json.get('folder')
    if not folder_name:
        return jsonify({'error': 'Folder name is required'}), 400

    new_folder = os.path.join(current_folder, folder_name)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
        return jsonify({'message': 'Folder created successfully'})
    return jsonify({'error': 'Folder already exists'}), 400


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to the current directory.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The file to upload
    responses:
      200:
        description: File uploaded successfully
      400:
        description: No file uploaded
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    file_path = os.path.join(current_folder, file.filename)
    file.save(file_path)
    return jsonify({'message': 'File uploaded successfully', 'filename': file.filename})


@app.route('/delete', methods=['DELETE'])
def delete_item():
    """
    Delete a file or folder in the current directory.
    ---
    parameters:
      - name: target
        in: body
        schema:
          type: object
          properties:
            target:
              type: string
              description: The file or folder name to delete
              example: "file_or_folder_name"
        required: true
    responses:
      200:
        description: Successfully deleted the item
        content:
          application/json:
            example:
              message: "Item deleted successfully"
      400:
        description: Item name is missing
        content:
          application/json:
            example:
              error: "Item name is required"
      404:
        description: Item does not exist
        content:
          application/json:
            example:
              error: "Item does not exist"
    """
    global current_folder
    target_name = request.json.get('target')

    
    if not target_name:
        return jsonify({'error': 'Item name is required'}), 400

    target_path = os.path.join(current_folder, target_name)

    
    if not os.path.exists(target_path):
        return jsonify({'error': 'Item does not exist'}), 404

    try:
        
        if os.path.isfile(target_path):
            os.remove(target_path)
        elif os.path.isdir(target_path):
            rmtree(target_path) 
        return jsonify({'message': 'Item deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete item: {str(e)}'}), 500

@app.route('/download', methods=['GET'])
def download_file():
    """
    Download a file from the current directory.
    ---
    parameters:
      - name: filename
        in: query
        type: string
        required: true
        description: The name of the file to download
    responses:
      200:
        description: File downloaded successfully
      400:
        description: Filename is missing
      404:
        description: File not found
    """
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    file_path = os.path.join(current_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(current_folder, filename, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/create-file', methods=['POST'])
def create_file():
    """
    Create a new file with content.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            file_name:
              type: string
            content:
              type: string
            directory:
              type: string
    responses:
      200:
        description: File created successfully
      400:
        description: File name or content is missing
    """
    data = request.json
    file_name = data.get('file_name')
    content = data.get('content')

    if not file_name or not content:
        return jsonify({'error': 'File name and content are required', "success": False}), 400

    directory = data.get('directory', BASE_DIR)
    result = manager.create_file(directory, file_name, content)

    return jsonify(result)


@app.route('/open-file', methods=['POST'])
def open_file():
    """
    Open a file and read its contents.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            file_name:
              type: string
            directory:
              type: string
    responses:
      200:
        description: File opened successfully
      400:
        description: File name is missing
    """
    data = request.json
    file_name = data.get('file_name')

    if not file_name:
        return jsonify({'error': 'File name is required', "success": False}), 400

    directory = data.get('directory', BASE_DIR)
    result = manager.open_file(directory, file_name)
    return jsonify(result)


@app.route('/move-file', methods=['POST'])
def move_file():
    """
    Move or copy a file from one folder to another.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            current_file_folder:
              type: string
              description: The full path to the file to be moved/copied.
              example: "home/ServerTask/files/begzad/text.txt"
            new_file_folder:
              type: string
              description: The destination folder where the file should be moved/copied.
              example: "home/ServerTask/files/ozod"
            cut:
              type: boolean
              description: Specify whether the file should be cut (True) or copied (False).
              example: true
    responses:
      200:
        description: File moved/copied successfully
        examples:
          application/json: {"message": "File moved/copied successfully"}
      400:
        description: Invalid input or file not found
        examples:
          application/json: {"error": "Source file does not exist"}
      404:
        description: Target folder not found
        examples:
          application/json: {"error": "Target folder does not exist"}
    """
    data = request.json
    current_file_folder = data.get('current_file_folder')
    new_file_folder = data.get('new_file_folder')
    cut = data.get('cut', False)  

    print(f"{current_file_folder} {new_file_folder} {cut}")

    if not current_file_folder or not new_file_folder:
        return jsonify({'error': 'Both current_file_folder and new_file_folder are required'}), 400

    if not os.path.exists(current_file_folder):
        return jsonify({'error': 'Source file does not exist'}), 400

    if not os.path.exists(new_file_folder) or not os.path.isdir(new_file_folder):
        return jsonify({'error': 'Target folder does not exist'}), 404

    # Get the file name from the current file path
    is_file = os.path.isfile(current_file_folder)
    file_name = os.path.basename(current_file_folder)
    destination_path = os.path.join(new_file_folder, file_name)

    try:
        if cut:
            # Move the file
            os.rename(current_file_folder, destination_path)
            message = "File moved successfully"
        else:
            if is_file:
                # Copy file
                copy2(current_file_folder, destination_path)
            else:
                # Copy folder
                copytree(current_file_folder, destination_path)
            message = "File/Folder copied successfully"

        return jsonify({'message': message, 'destination_path': destination_path})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/rename', methods=['POST'])
def rename_item():
    """
    Rename a file or folder.
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            current_name:
              type: string
              description: The current name of the file or folder.
              example: "old_name.txt"
            new_name:
              type: string
              description: The new name for the file or folder.
              example: "new_name.txt"
        required:
          - current_name
          - new_name
    responses:
      200:
        description: Item renamed successfully.
        examples:
          application/json: {"message": "Item renamed successfully"}
      400:
        description: Missing or invalid input.
        examples:
          application/json: {"error": "Name not provided or invalid"}
      404:
        description: Item not found.
        examples:
          application/json: {"error": "Item not found"}
    """
    data = request.json
    current_name = data.get('current_name')
    new_name = data.get('new_name')

    if not current_name or not new_name:
        return jsonify({'error': 'Both current_name and new_name are required'}), 400

    current_path = os.path.join(current_folder, current_name)
    new_path = os.path.join(current_folder, new_name)

    if not os.path.exists(current_path):
        return jsonify({'error': 'Item not found'}), 404

    try:
        os.rename(current_path, new_path)
        return jsonify({'message': 'Item renamed successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to rename item: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# File Upload and Management Application.

Flask File Upload and Management Application. 

This document provides an overview of the Flask File Upload and Management Application, 
a simple web application that allows users to upload, view, and manage their files.


Features

- User registration and login
- Uploading files
- Viewing user's own files
- Viewing all uploaded files (only available for logged-in users)
- Adding files to favorites (only available for logged-in users)
- Viewing and managing favorites (only available for logged-in users)

## installation and run
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

and go to http://localhost:8080/

## file structure
```yaml
- models.py
- app.py
- utils.py
- Procfile
- runtime.txt
- requirements.txt
- .gitignore
- templates
    - auth
      - login.html
      - register.html
    - files
      - files.html
    - home
      - index.html
- static 
- instance
    - users.db
```



Routes additionally works with templates, we have also following endpoints:
## endpoints

### /api/register - POST
```json
{
    "username": "username",
    "email": "email",
    "password": "password"
}
```
#### status code - 201
```json
{
  "message": "User created successfully"
}
```

-----------------

### /api/login - POST
```json
{
    "username": "username",
    "password": "password"
  
}
```
#### status code - 200
```json
{
  "message": "User logged in successfully"
}
```
#### status code - 400
```json
{
  "error": "Invalid username or password"
}
```

### /api/logout - POST
#### status code - 200
```json
{
  "message": "User logged out successfully"
}
```

### /api/upload - POST /multipart-form-data
#### status code - 201
```json
{
  "message": "File uploaded successfully"
}
```
#### status code - 400
```json
{
  "message": "File upload failed"
}
```

### /api/files - GET
#### status code - 401
```json
{
  "error": "Unauthorized"
}
```
#### status code - 200
```json
[
  {
    "name": "name",
    "document_link": "link",
    "doc_size": "size"
  },
  {
    "name": "name",
    "document_link": "link",
    "doc_size": "size"
  }
]
```

### /api/all_files - GET
#### status code - 401
```json
{
  "error": "Unauthorized"
}
```
#### status code - 200
```json
[
  {
    "name": "name",
    "document_link": "link",
    "doc_size": "size"
  },
  {
    "name": "name",
    "document_link": "link",
    "doc_size": "size"
  }
]
```
### /api/files - GET
#### status code - 401
```json
{
  "error": "Unauthorized"
}
```
#### status code - 200
```json
[
  {
    "name": "name",
    "document_link": "link",
    "doc_size": "size"
  },
  {
    "name": "name",
    "document_link": "link",
    "doc_size": "size"
  }
]
```
  
### /api/like/{document_id} - GET
#### status code - 404
```json
{
  "error": "Not found"
}
```

#### status code - 201
```json
{
  "error": "Document liked successfully"
}
```

### /api/delete/{document_id} - GET
#### status code - 404
```json
{
  "error": "Not found"
}
```
#### status code - 201
```json
{
  "error": "Document deleted successfully"
}
```

The application uses SQLAlchemy to interact with the SQLite database that stores the user and file information.
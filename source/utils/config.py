class Config:
    SECRET_KEY =  'senha'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_PORT = 3306
    MYSQL_DB = 'gradmate'
    JWT_SECRET_KEY = 'senhajwt'
    # Uploads
    UPLOAD_FOLDER = 'uploads'  # base folder (relative to project root). Files will be stored under uploads/projects/<project_id>
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024  # 64MB per request (adjust as needed)
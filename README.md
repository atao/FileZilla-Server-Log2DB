[![Lint Python](https://github.com/atao/FileZilla-Server-Log2DB/actions/workflows/main.yml/badge.svg)](https://github.com/atao/FileZilla-Server-Log2DB/actions/workflows/main.yml)
# FileZilla-Server-Log2DB
The purpose of this script is to parse the FileZilla Server logs and insert them in a Sqlite database.

### Installation
```
git clone https://github.com/atao/FileZilla-Server-Log2DB.git
cd FileZilla-Server-Log2DB
pip install -r requirements.txt
```
### Configuration
Edit the script to modify variables to specify the location of FileZilla Server logs.
By default the script scans the last two log files.

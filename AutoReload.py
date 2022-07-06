#!/usr/bin/python3

"""
USAGE:
	Copy this server file into your project folder and run it
	After running server copy this
	<script src="check_files.js?ms=500"></script>
	into your HTML file in which you wants add auto reload functionality
	
	ms=500 means your JavaScript will send request to server after every 500 milliseconds
	to check if any file is updated or not
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import mimetypes
import os
#  import time

class AutoReload(SimpleHTTPRequestHandler):
	check_file_js = """function checkFiles() {{
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {{
        if (this.readyState == 4 && this.status == 200)
            if (this.responseText === "1") location.reload()
    }};
    xhttp.open("GET", "check_files", true);
    xhttp.send();
}}
setInterval(checkFiles, {0})"""
	file_changed = False # Static variable to check if any file has been changed or not
	def do_GET(self):
		#  time.sleep(3)
		queries = {}
		query_index = self.path.find("?")
		if query_index != -1:
			query_list = self.path[query_index+1:].split("&")
			for q in query_list:
				query = q.split("=")
				if len(query) == 2:
					queries[query[0]] = query[1]
			path = self.path[1:query_index]
		else:
			path = self.path[1:]
		if path == "check_files": # Auto Reload api
			self.checkFiles()
			self.sendData(str(int(self.file_changed)).encode(), 200)
			self.file_changed = False
		elif path == "check_files.js":
			ms = queries.get("ms")
			if not ms:
				ms = 600
			file_js = self.check_file_js.format(ms)
			self.sendData(file_js.encode(), 200, "application/javascript")
		elif os.path.isfile(path): # Any file which has been requested
			MimeType = mimetypes.MimeTypes().guess_type(path)[0]
			file_data = AllFilesData[path]
			self.sendData(file_data, 200, MimeType)
		elif not path and os.path.isfile("index.html"): # If path or URL does not contain anything then return index.html file
			file_data = readFile("index.html")
			self.sendData(file_data, 200, "text/html")
		else: # If index.html file does not exist then send error message
			self.sendData("No Such File".encode(), 404)

	# Send data back to web browser with the given data, file Mime Type and code
	def sendData(self, file_data, code, MimeType=None):
		if not MimeType:
			MimeType = "text/plain"
		self.send_response(code)
		self.send_header("Content-type", MimeType)
		self.end_headers()
		self.wfile.write(file_data)

	# Check and update file_changed if any file has been updated
	def checkFiles(self):
		global AllFilesData
		NewFilesData = self.readEveryFile()
		if AllFilesData != NewFilesData:
			AllFilesData = NewFilesData
			self.file_changed = True

	# Read every file located in project/current directory
	def readEveryFile(self):
		NewFilesData = {}
		for f in dirTree():
			NewFilesData[f] = readFile(f)
		return NewFilesData
	
	def log_message(self, format, *args):
		pass


# Return full path of every single file in project/current directory
def dirTree():
    path = ""
    current_files = []
    current_dirs = ["."]
    for p in current_dirs:
        for f in os.listdir(p):
            if p != ".":
                path = p
            if path:
                path += "/" + f
            else:
                path = f
            if os.path.isfile(path):
                current_files.append(path)
            elif os.path.isdir(path):
                current_dirs.append(path)
            path = ""
    return current_files


# Read whole file and return readed data
def readFile(path):
	with open(path, "rb") as file:
		file_data = file.read()
	return file_data


def serve():
	HOST = ""
	PORT = 8000
	server = HTTPServer((HOST, PORT), AutoReload)
	print(f"Serving at {HOST}:{PORT}")
	server.serve_forever()


AllFilesData = {} # Global Dictionary Variable which will contain every file data along its path
def main():
	for f in dirTree():
		AllFilesData[f] = readFile(f)
	serve()

main()

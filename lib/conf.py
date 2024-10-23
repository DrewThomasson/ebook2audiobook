import os

version = "2.0.0"

min_python_version = (3, 10)
max_python_version = (3, 11)

docker_utils_image = 'utils'
web_interface_port = 7860
web_dir_expire = 72 # hours

model_root = os.path.abspath("./models")
ebooks_dir = os.path.abspath("./ebooks")
audiobooks_dir = os.path.abspath("./audiobooks")
process_dir = os.path.abspath("./tmp")

supported_ebook_formats = ['.epub', '.mobi', '.azw3', 'fb2', 'lrf', 'rb', 'snb', 'tcr', '.pdf', '.txt', '.rtf', '.docx', '.html', '.odt', '.azw']
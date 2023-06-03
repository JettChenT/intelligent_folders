import magic

class FileInfo:
    def __init__(self, filename:str) -> None:
        self.filename = filename
        self.filetype = magic.from_file(filename)
    
    def describe(self) -> str:
        return f'the filename is: {self.filename}\n the identified filetype of the file is: {self.filetype}'
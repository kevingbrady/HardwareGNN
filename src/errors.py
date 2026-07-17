class YosysSynthesisError(Exception):
    exit_code = 1
    def __init__(self, process_output):
        super(YosysSynthesisError, self).__init__(process_output)
        self.process_output = process_output

class TCLError(Exception):
    exit_code = 1
    def __init__(self, message):
        super(TCLError, self).__init__(message)
        self.message = message


params_error = "some params error? more info can be found in data."
operate_success = "operate success."
operate_fail = "operate failed."
db_fail = "db operate failed, please contact admin."


class WebCode(object):
    Ok = 0
    ParameterError = -1
    UnAuth = -2
    ServerError = -3
    InterfaceError = -4
    AssertError = -5
    DbError = -6
    RemoteReqError = -7
    CheckError = -8

class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class FileNotFoundException(Exception):
    def __init__(self, msg):
        self.message = msg

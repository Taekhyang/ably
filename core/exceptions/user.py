from core.exceptions import CustomException


class DuplicateUserException(CustomException):
    code = 409
    error_code = "USER__ALREADY_EXIST"
    message = "user already exist"


class SMSSenderException(CustomException):
    code = 504
    error_code = "SMS__NOT_SENT"
    message = "sms message send failure"


class SMSAuthTimeoutException(CustomException):
    code = 401
    error_code = "SMS__AUTH_CODE_TIMEOUT"
    message = "sms auth code input timeout"


class SMSAuthCodeNotMatchedException(CustomException):
    code = 401
    error_code = "SMS__AUTH_CODE_NOT_MATCHED"
    message = "sms auth code mismatch"

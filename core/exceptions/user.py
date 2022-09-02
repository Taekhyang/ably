from core.exceptions import CustomException


class SMSSenderException(CustomException):
    code = 400
    error_code = "SMS__NOT_SENT"
    message = "sms message send failure"


class SMSAuthTimeoutException(CustomException):
    code = 400
    error_code = "SMS__AUTH_CODE_TIMEOUT"
    message = "sms auth code timeout"

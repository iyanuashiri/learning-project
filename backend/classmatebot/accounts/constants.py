from enum import Enum


class Message(Enum):
    INVALID_CREDENTIALS_ERROR = 'Email and password combination is not correct.'
    INACTIVE_ACCOUNT_ERROR = "User account is disabled."
    INVALID_TOKEN_ERROR = "Invalid token for given user."
    INVALID_UID_ERROR = "Invalid user id or user doesn't exist."
    NON_UNIQUE_EMAIL = "Oops! This email already exists."
    NON_UNIQUE_PHONE_NUMBER = "Oops! This phone number already exists."
    CANNOT_CREATE_USER_ERROR = "Unable to create account."
    EMAIL_NOT_FOUND = "User with given email does not exist."
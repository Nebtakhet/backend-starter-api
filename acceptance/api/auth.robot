*** Settings ***
Resource    ../resources/api.resource
Suite Setup    Create API Session
Suite Teardown    Delete All Sessions

*** Test Cases ***
User Can Register And Login
    Create Test User
    Login As Test User
    Should Not Be Empty    ${AUTH_HEADERS}[Authorization]

Invalid Login Is Rejected
    Create Test User
    ${payload}=    Create Dictionary
    ...    email=${TEST_EMAIL}
    ...    password=WrongPassword123!
    ${response}=    POST On Session
    ...    api
    ...    /api/v1/auth/login
    ...    json=${payload}
    ...    expected_status=401
    Response Body Should Contain Error Code    ${response}    auth_error
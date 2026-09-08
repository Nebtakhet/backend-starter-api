*** Settings ***
Library    Collections
Library    RequestsLibrary
Library    String

*** Keywords ***
Create API Session
    Create Session    api    ${BASE_URL}

Create Test User
    ${random}=    Generate Random String    12    [LOWER]
    ${email}=    Set Variable    robot-${random}@example.com
    ${password}=    Set Variable    RobotPassword123!
    ${payload}=    Create Dictionary    email=${email}    password=${password}
    ${response}=    POST On Session
    ...    api
    ...    /api/v1/users/
    ...    json=${payload}
    ...    expected_status=201
    Set Suite Variable    ${TEST_EMAIL}    ${email}
    Set Suite Variable    ${TEST_PASSWORD}    ${password}

Login As Test User
    ${payload}=    Create Dictionary
    ...    email=${TEST_EMAIL}
    ...    password=${TEST_PASSWORD}
    ${response}=    POST On Session
    ...    api
    ...    /api/v1/auth/login
    ...    json=${payload}
    ...    expected_status=200
    ${body}=    Set Variable    ${response.json()}
    ${access_token}=    Set Variable    ${body}[access_token]
    ${headers}=    Create Dictionary    Authorization=Bearer ${access_token}
    Set Suite Variable    ${AUTH_HEADERS}    ${headers}

Response Body Should Contain Error Code
    [Arguments]    ${response}    ${expected_code}
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${body}[code]    ${expected_code}
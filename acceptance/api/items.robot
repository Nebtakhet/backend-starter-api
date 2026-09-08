*** Settings ***
Resource    ../resources/api.resource
Suite Setup    Create API Session
Suite Teardown    Delete All Sessions

*** Test Cases ***
Authenticated User Can Create And List An Item
    Create Test User
    Login As Test User
    ${payload}=    Create Dictionary
    ...    title=Robot acceptance item
    ...    description=Created through the public API
    ${create_response}=    POST On Session
    ...    api
    ...    /api/v1/items/
    ...    json=${payload}
    ...    headers=${AUTH_HEADERS}
    ...    expected_status=201
    ${created}=    Set Variable    ${create_response.json()}
    Should Be Equal As Strings    ${created}[title]    Robot acceptance item

    ${list_response}=    GET On Session
    ...    api
    ...    /api/v1/items/
    ...    headers=${AUTH_HEADERS}
    ...    expected_status=200
    ${listed}=    Set Variable    ${list_response.json()}
    Should Be True    ${listed}[total] >= 1

Unauthenticated User Cannot Access Items
    ${response}=    GET On Session
    ...    api
    ...    /api/v1/items/
    ...    expected_status=401
    Response Body Should Contain Error Code    ${response}    auth_error
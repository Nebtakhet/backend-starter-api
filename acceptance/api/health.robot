*** Settings ***
Resource    ../resources/api.resource
Suite Setup    Create API Session
Suite Teardown    Delete All Sessions

*** Test Cases ***
API Is Live
    ${response}=    GET On Session
    ...    api
    ...    /health/live
    ...    expected_status=200
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${body}[status]    ok

API Is Ready
    ${response}=    GET On Session
    ...    api
    ...    /health/ready
    ...    expected_status=200
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal As Strings    ${body}[database]    connected
*** Settings ***
Library      ../library/ClientLibrary.py
Variables    ../config/variables.py


*** Keywords ***
Step 1 Connect to db
    connect to db
Step 2 Get balance of client positive
    get balance positive
Step 3 Get client services
    [Arguments]  ${url}
    get client services    ${url}
Step 4 Get services
   [Arguments]  ${url}
   get services  ${url}
Step 5 Get external service
    get unused services
Step 6 Set new service for client
    [Arguments]  ${url}
    set client service  ${url}
Step 7 Waiting for a new service to be installed
    [Arguments]  ${url}
    wait new service  ${url}
Step 8 Get end balance of client
    get balance
Step 9 Attemp compare start end balance
    compare start end balance


*** Test Cases ***
Test 1 Connect to db
    Step 1 Connect to db
#    Status should be  SUCCESS

Test 2 Get balance
    Step 2 Get balance of client positive
#    Status should be  SUCCESS

Test 3 Get client services
    Step 3 Get client services    ${URL}
#    Status should be  200

Test 4 Get services
    Step 4 Get services  ${URL}
#    Status should be  200

Test 5 Get external service
    Step 5 Get external service
#    Status should be  SUCCESS

Test 6 Set new service for client
    Step 6 Set new service for client  ${URL}
#    Status should be  202

Test 7 Waiting for a new service
    Step 7 Waiting for a new service to be installed  ${URL}
#    Status should be  SUCCESS

Test 8 Get end balance of client
    Step 8 Get end balance of client
#    Status should be  SUCCESS

Test 9 Compare start end balance of client
    Step 9 Attemp compare start end balance
#    Status should be  UNSUCCESS

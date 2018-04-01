*** Settings ***
Library      ../sut/ClientLibrary.py
Variables    ../config/config.py


*** Keywords ***
Step 1 Connect to db
    get connect to db
Step 2 Get balance of client positive
    get balance positive
Step 3 Get client services
    [Arguments]  ${port}
    get client services    ${port}
Step 4 Get services
   [Arguments]  ${port}
   get services  ${port}
Step 5 Get external service
    get ex services
Step 6 Set new service for client
    [Arguments]  ${port}
    set client service  ${port}
Step 7 Waiting for a new service to be installed
    [Arguments]  ${port}
    wait new service  ${port}
Step 8 Get end balance of client
    get end balance
Step 9 Attemp compare start end balance
    compare start end balance


*** Test Cases ***
Test 1 Connect to db
    Step 1 Connect to db
    Status should be  SUCCESS

Test 2 Get balance
    Step 2 Get balance of client positive
    Status should be  SUCCESS

Test 3 Get client services
    Step 3 Get client services    ${PORT}
    Status should be  200

Test 4 Get services
    Step 4 Get services  ${PORT}
    Status should be  200

Test 5 Get external service
    Step 5 Get external service
    Status should be  SUCCESS

Test 6 Set new service for client
    Step 6 Set new service for client  ${PORT}
    Status should be  202

Test 7 Waiting for a new service
    Step 7 Waiting for a new service to be installed  ${PORT}
    Status should be  SUCCESS

Test 8 Get end balance of client
    Step 8 Get end balance of client
    Status should be  SUCCESS


Test 9 Compare start end balance of client
    Step 9 Attemp compare start end balance
    Status should be  UNSUCCESS

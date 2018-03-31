*** Settings ***
Library       /home/mark/PycharmProjects/ps_test_task/sut/clients.py


*** Variables ***
${PORT}     5000
${POSITIVE_RESULT}    Success


*** Keywords ***
Step 1 Connect to db
    get connect step
Step 2 Get balance of client positive
    get balance positive
Step 3 Get client services
    [Arguments]  ${port}
    get client services     ${port}
Step 4 Get services
   [Arguments]  ${port}
   get services  ${port}
Step 5 Get external service
    get external service

Step 6 Set new service for client
    [Arguments]  ${port}
    set client service  ${port}
Step 7 Waiting for a new service to be installed
    [Arguments]  ${port}
    wait new service  ${port}
Step 8 Get end balance of client
    get end balance
Step 9 Compare start end balance
    compare start end balance


*** Test Cases ***
Test 1 Connect to db
    Step 1 Connect to db

Test 2 Get balance
    Step 2 Get balance of client positive

Test 3 Get client services
    Step 3 Get client services    ${PORT}

Test 4 Get services
    Step 4 Get services  ${PORT}

Test 5 Get external service
    Step 5 Get external service

Test 6 Set new service for client
    Step 6 Set new service for client  ${PORT}

Test 7 Waiting for a new service
    Step 7 Waiting for a new service to be installed  ${PORT}

Test 8 Get end balance of client
    Step 8 Get end balance of client

Test 9 Compare start end balance of client
    Step 9 Compare start end balance
*** Settings ***
Variables    ../config/variables.py
Library      ../library/ClientLibrary.py  ${HOST}  ${PORT}
Test Setup     Connect to db  ${DATABASE_PATH}
Test Teardown  Close db


*** Test Cases ***
Test case
    ${client_balance}       Take add client with positive balance    ${BALANCE_FOR_NEW_CLIENT}
    ${client_services}      Get client services                      ${client_balance}
    ${services}             Get services
    ${service_id}  ${service_cost}       Get unused service                      ${client_services}  ${services}
                            Set client service                       ${client_balance}  ${service_id}
                            Wait new service                         ${client_balance}  ${service_id}  ${WAIT_TIME}
    ${current_balance}      Get client balance                      ${client_balance}
#                            Should be equal                          @{balanses}[0]  @{balanses}[1]  Expected balance of client to be @{balanses}[0] but was @{balanses}[1]  values=False
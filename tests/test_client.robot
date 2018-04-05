*** Settings ***
Variables    ../config/variables.py
Library      ../library/ClientLibrary.py  ${HOST}  ${PORT}
Test Setup     Connect to db  ${DATABASE_PATH}
Test Teardown  Close db


*** Test Cases ***
Test case
    ${client_id}  ${start_balance}  Take add client with positive balance  ${BALANCE_FOR_NEW_CLIENT}
    ${client_services}              Get client services                    ${client_id}
    ${services}                     Get services
    ${service_id}  ${service_cost}  Get unused service                     ${client_services}  ${services}
                                    Set client service                     ${client_id}  ${service_id}
                                    Wait new service                       ${client_id}  ${service_id}  ${WAIT_TIME}
    ${current_balance}              Get client balance                     ${client_id}
                                    Check balance reduced to service cost  ${start_balance}  ${current_balance}  ${service_cost}
*** Settings ***
Library      ../library/ClientLibrary.py  ${HOST}  ${PORT}
Test Setup     Connect to db  ${DATABASE_PATH}
Test Teardown  Close db


*** Test Cases ***
Test case
    ${client_id}  ${start_balance}  Create or get existing client with positive balance  ${BALANCE_FOR_NEW_CLIENT}
    ${client_services}              Get client services                    ${client_id}
    ${services}                     Get services
    ${service_id}  ${service_cost}  Get unused service                     ${client_services}  ${services}
                                    Add new service to client              ${client_id}  ${service_id}
                                    Wait appear new service for client     ${client_id}  ${service_id}  ${WAIT_TIME}
    ${current_balance}              Get client balance                     ${client_id}
                                    Check balance reduced to service cost  ${start_balance}  ${current_balance}  ${service_cost}



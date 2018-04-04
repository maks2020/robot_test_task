*** Settings ***
Library      ../library/ClientLibrary.py
Variables    ../config/variables.py
Suite Setup  Connect to db


*** Test Cases ***
Test case
    ${client_balance}       Get client with positive balance  ${BALANCE_FOR_NEW_CLIENT}
    ${client_services}      Get client services               ${URL}  ${client_balance}
    ${services}             Get services                      ${URL}
    ${unused_service}       Get unused services               ${client_services}  ${services}
                            Set client service                ${URL}  ${client_balance}  ${unused_service}
                            Wait new service                  ${URL}  ${client_balance}  ${unused_service}  ${WAIT_TIME}
    @{balanses}             Get client balances               ${client_balance}  ${unused_service}
                            Should be equal                   @{balanses}[0]  @{balanses}[1]  Expected balance of client to be @{balanses}[0] but was @{balanses}[1]  values=False
*** Settings ***
Library      ../library/ClientLibrary.py
Variables    ../config/variables.py
Suite Setup  Connect to db


*** Test Cases ***
Test case
    ${client_balance}       Get client with positive balance
    ${client_services}      Get client services               ${URL}  ${client_balance}
    ${services}             Get services                      ${URL}
    ${unused_service}       Get unused services               ${client_services}  ${services}
                            Set client service                ${URL}  ${client_balance}  ${unused_service}
                            Wait new service                  ${URL}  ${client_balance}  ${unused_service}  ${WAIT_TIME}
    @{balanses_and_errmsg}  Get client balances               ${client_balance}  ${unused_service}
                            Should be equal                   @{balanses_and_errmsg}[0]  @{balanses_and_errmsg}[1]  @{balanses_and_errmsg}[2]  values=False
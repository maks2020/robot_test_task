*** Settings ***
Library      ../library/ClientLibrary.py
Variables    ../config/variables.py
Suite Setup  Connect to db


*** Test Cases ***
Test case
    ${client_balance}         Get client with positive balance
    ${client_services}        Get client services                ${URL}  ${client_balance}
    ${services}               Get services                       ${URL}
    ${unused_service}         Get unused services                ${client_services}  ${services}
                              Set client service                 ${URL}  ${client_balance}  ${unused_service}
                              Wait new service                   ${URL}  ${client_balance}  ${unused_service}
    ${current_balance}        Get client balance                 ${client_balance}
                              Compare start end balance          ${client_balance}  ${unused_service}  ${current_balance}

*** Settings ***
Library      ../library/ClientLibrary.py
Variables    ../config/variables.py


*** Test Cases ***
Test case
    Connect to db
    Get client with positive balance
    Get client services    ${URL}
    Get services           ${URL}
    Get unused services
    Set client service     ${URL}
    Wait new service       ${URL}
    Get client balance
    Compare start end balance

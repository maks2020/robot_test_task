*** Settings ***
Library      ../library/ClientLibrary.py
Variables    ../config/variables.py


*** Test Cases ***
Test case
    Connect to db
    Get client balance positive
    Get client services    ${URL}
    Get services           ${URL}
    Get unused services
    Set client service     ${URL}
    Wait new service       ${URL}
    Get balance
    Compare start end balance

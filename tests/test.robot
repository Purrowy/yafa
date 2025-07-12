*** Settings ***
Documentation    YAFA Tests
Library    SeleniumLibrary
Test Setup    Open Application
Test Teardown    Close Browser

*** Variables ***
${url}    http://127.0.0.1:5000
${amount_field}    id=amount
${submit_button}    id=submit
${last_transaction_locator}   xpath=/html/body/table[3]/tbody/tr[2]/td[1]
${total_amount_locator}    id=total_amount
${acc_manager_button}    xpath=//*[@id="acc_manager_url"]
${last_acc_id}    xpath=/html/body/table[3]/tbody/tr[2]/td[1]

*** Test Cases ***
Main Page
    Submit Transaction

Account Manager
    Navigate To Acc Manager
    Update Total
    Add New Account

*** Keywords ***
Submit Transaction
    ${orig_last_tr_id}    Get Last Transaction ID
    ${orig_total}    Get Total Amount
    Input Text    ${amount_field}    10
    Click Button    ${submit_button}
    Wait Until Element Is Visible    ${last_transaction_locator}    timeout=5s
    ${new_last_tr_id}    Get Last Transaction ID
    ${new_total}    Get Total Amount
    Should Not Be Equal    ${orig_last_tr_id}    ${new_last_tr_id}
    Should Not Be Equal    ${orig_total}    ${new_total}

Get Last Transaction ID
    ${id}    Get Text    ${last_transaction_locator}
    RETURN    ${id}

Get Total Amount
    ${total}    Get Text    ${total_amount_locator}
    RETURN    ${total}    
    
Open Application
    Open Browser        ${url}    Chrome
    Wait Until Element Is Visible    ${amount_field}    timeout=5s

Update Total
    Input Text    id=amount_1    15
    Click Button    id=submit_1
    Sleep    2
    ${new_amount}    Get Value    id=amount_1
    Should Be Equal As Numbers   ${new_amount}    15.00
    Revert Changes

Add New Account
    Input Text    id=new_acc_bank    Test Bank
    Input Text    id=new_acc_name    Test
    Input Text    id=new_acc_amount    999
    Click Button    id=add_account_button
    Sleep    2
    Page Should Contain    Test Bank

Revert Changes
    Input Text    id=amount_1    100
    Click Button    id=submit_1

Navigate to Acc Manager
    Click Element    ${acc_manager_button}
    Wait Until Element Is Visible    xpath=/html/body/h2
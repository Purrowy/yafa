document.getElementById("header_acc").addEventListener("click", getTableData)

// https://javacodepoint.com/read-html-table-data-in-javascript/
function getTableData()
{
    let table = document.getElementById("report_table")
    if (table != null) {
        console.log("ayy");
    }

    // loop thru rows
    for (let i = 0; i < table.rows.length; i++) {
        let row = table.rows[i]
        console.log(row)
    }
        // loop thru cells
}
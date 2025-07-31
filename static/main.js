document.getElementById("header_id").innerHTML = "Test"
let tableInner = document.getElementById("report_table").innerHTML
document.getElementById("header_acc").addEventListener("click", getTableData(tableInner))

// https://javacodepoint.com/read-html-table-data-in-javascript/
function getTableData(table)
{
    if (table != null) {
        console.log("ayy");
    }
}

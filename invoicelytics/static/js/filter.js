function filterTable() {
    var dateFilter = document.getElementById("dateFilter").value.toLowerCase();
    var descriptionFilter = document.getElementById("descriptionFilter").value.toLowerCase();
    var amountFilter = document.getElementById("amountFilter").value.toLowerCase();
    var cardEndingFilter = document.getElementById("cardEndingFilter").value.toLowerCase();
    var itemFilter = document.getElementById("itemFilter").value.toLowerCase();
    var categoryFilter = document.getElementById("categoryFilter").value.toLowerCase();
    var subCategoryFilter = document.getElementById("subCategoryFilter").value.toLowerCase();

    var table = document.getElementById("transactionsTable");
    var tr = table.getElementsByTagName("tr");

    for (var i = 2; i < tr.length; i++) {
        var tdDate = tr[i].getElementsByTagName("td")[0];
        var tdDescription = tr[i].getElementsByTagName("td")[1];
        var tdAmount = tr[i].getElementsByTagName("td")[2];
        var tdCardEnding = tr[i].getElementsByTagName("td")[3];
        var tdItem = tr[i].getElementsByTagName("td")[4];
        var tdCategory = tr[i].getElementsByTagName("td")[5];
        var tdSubCategory = tr[i].getElementsByTagName("td")[6];

        if (tdDate && tdDescription && tdAmount && tdCardEnding && tdItem && tdCategory && tdSubCategory) {
            var dateValue = tdDate.textContent || tdDate.innerText;
            var descriptionValue = tdDescription.textContent || tdDescription.innerText;
            var amountValue = tdAmount.textContent || tdAmount.innerText;
            var cardEndingValue = tdCardEnding.textContent || tdCardEnding.innerText;
            var itemValue = tdItem.getElementsByTagName("input")[0].value;
            var categoryValue = tdCategory.getElementsByTagName("select")[0].value;
            var subCategoryValue = tdSubCategory.getElementsByTagName("select")[0].value;

            if (dateValue.toLowerCase().indexOf(dateFilter) > -1 &&
                descriptionValue.toLowerCase().indexOf(descriptionFilter) > -1 &&
                amountValue.toLowerCase().indexOf(amountFilter) > -1 &&
                cardEndingValue.toLowerCase().indexOf(cardEndingFilter) > -1 &&
                itemValue.toLowerCase().indexOf(itemFilter) > -1 &&
                categoryValue.toLowerCase().indexOf(categoryFilter) > -1 &&
                subCategoryValue.toLowerCase().indexOf(subCategoryFilter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
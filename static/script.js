function setup() {
	document.getElementById("categoryButton").addEventListener("click", addCategory, true);
	document.getElementById("purchaseButton").addEventListener("click", addPurchase, true);
	document.getElementById("submitDeleteButton").addEventListener("click", deleteCateogry, true);
	initializePage();
	poller();
}

function initializePage(){
	var d = new Date();
	var n = d.getMonth();
	var month; 
	switch (n) {
		case 0: 
			month = "January"
			break; 
		case 1: 
			month = "February"
			break; 
		case 2: 
			month = "March"
			break; 
		case 3: 
			month = "April"
			break; 
		case 4: 
			month = "May"
			break; 
		case 5: 
			month = "June"
			break; 
		case 6: 
			month = "July"
			break; 
		case 7: 
			month = "August"
			break; 
		case 8: 
			month = "September"
			break; 
		case 9: 
			month = "October"
			break; 
		case 10:
			month = "November"
			break;
		case 11: 
			month = "December"
			break; 
	}
	document.getElementById("currentMonth").innerHTML = "Current Month Is: " + month;
}

function poller() {
	makeRequest("GET", "/cats", 200, repopulateCategory);
	makeRequest("GET", "/cats", 200, repopulateDropDownMenu);
}

function repopulatePurchase(responseText) {
	var purchases = JSON.parse(responseText);;
	var allCategories = JSON.parse(responseText);;
	console.log("Response text in repopulatePurchase: " + responseText); 

	//Figuring out which categories have been deleted
	const listOfCategories = allCategories.map(cat => cat.category);
	var categoryList = [];
	var table = document.getElementById("theTable");
	for (var i = 2; i<table.rows.length; i++) {
		let row = table.rows[i]
			for (var j = 0; j<1; j++) {
			  let col = row.cells[j]
			  categoryList.push(col.innerHTML)
			}
		}
	var deletedCats = listOfCategories.filter(cat => listOfCategories.includes(cat) && !categoryList.includes(cat))

	//Actually repopulating the table
	var table = document.getElementById("theTable");
	for (var i = 2; i<table.rows.length; i++) {
		   let row = table.rows[i]
  		 	for (var j = 0; j<1; j++) {
				 let col = row.cells[j]
				 categoryList.push((col).innerHTML)
				 var currentRow = col.innerHTML.trim(); 
					sum = {amount: 0}
					var currentCategory = purchases.filter(function (currentPurchase) {
						if (deletedCats.includes(currentPurchase.category.trim())) {
							currentPurchase.category = "Uncategorized" }
						if (currentPurchase.category.trim() == currentRow) {
							return true; }
						else {
							return false; }
					});
					if (currentCategory.length > 0)
					{
					sum = currentCategory.reduce(function(priorSum, currentSum){
						return {amount: parseFloat(priorSum.amount) + parseFloat(currentSum.amount)}
					});
					}
					addCell(row, sum.amount)
					if (currentRow=="Uncategorized")
					{
						addCell(row, "N/A")
						break;
					}
					if (row.cells[j+1].innerHTML-sum.amount >= 0)
						addCell(row, row.cells[j+1].innerHTML-sum.amount)
					else 
						addCell(row, "Overspent! :( ")
   			}  
	}
}

function makeRequest(method, target, retCode, action, data) {
	var httpRequest = new XMLHttpRequest();
	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	httpRequest.onreadystatechange = makeHandler(httpRequest, retCode, action);
	httpRequest.open(method, target);
	if (data){
		httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		httpRequest.send(data);
	}
	else {
		httpRequest.send();
	}
}

function makeHandler(httpRequest, retCode, action) {
	function handler() {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
			if (httpRequest.status === retCode) {
				//console.log("recieved response text:  " + httpRequest.responseText);
				action(httpRequest.responseText);
			} else {
				alert("There was a problem with the request.  you'll need to refresh the page!");
			}
		}
	}
	return handler;
}

function deleteCateogry(){
	var categoryToDelete = document.getElementById("categories").value
	makeRequest("DELETE", "/cats/" + categoryToDelete.trim(), 204, poller);
}

function addCategory(){
	var newCat = document.getElementById("categoryName").value;
	var categoryValue = document.getElementById("categoryValue").value;
	var data;
	data = "categoryName=" + newCat + "&categoryValue=" + categoryValue;
	makeRequest("POST", "/cats", 201,  poller, data);
	document.getElementById("categoryForm").reset();
}

function repopulateDropDownMenu(responseText)
{
	var cats = JSON.parse(responseText);
	//console.log("Response text in repopulateDropDownMeneu: " + responseText);
	document.getElementById("categories").length = 0;
	for (var t in cats) 
	{
		if (cats[t][0]=="Uncategorized")
		{
			continue; 
		}
		var x = document.getElementById("categories");
		var option = document.createElement("option");
		option.text = cats[t][0];
		x.add(option);
	}
	document.getElementById("categoriesSelect").length = 0;
	for (var t in cats) 
	{
		var x = document.getElementById("categoriesSelect");
		var option = document.createElement("option");
		option.text = cats[t][0];
		x.add(option);
	}
}

function addCell(row, text)
{
	var newCell = row.insertCell();
	var newText = document.createTextNode(text);
	newCell.appendChild(newText);
}

function addPurchase(){
	var newCategory = document.getElementById("categoriesSelect").value;
	var puchaseDate = document.getElementById("purchaseDate").value;
	var purchaseName = document.getElementById("purchaseName").value;
	var amountSpent = document.getElementById("amountSpent").value;
	data = "categoryName=" + newCategory + "&purchaseDate=" + puchaseDate + "&purchaseName=" + purchaseName + "&amountSpent=" + amountSpent;
	makeRequest("POST", "/purchases", 201, poller, data);
	document.getElementById("purchaseForm").reset();
}


function repopulateCategory(responseText) {
	//clear rows out of table 
	var cats = JSON.parse(responseText);
	console.log("Response text in repopulateCategory " + responseText);
	var table = document.getElementById("theTable");
	newRow = table.insertRow();
	while (table.rows.length > 1) {
		table.deleteRow(0);
	}
	newRow = table.insertRow();
	addCell(newRow, "CATEGORY NAME: ");
	addCell(newRow, "CATEGORY LIMIT: ");
	addCell(newRow, "SPENT: ");
	addCell(newRow, "REMAINING: ");
	for(var t in cats)
	{
		if (cats[t][0] == "Uncategorized")
		{
			newRow = table.insertRow();
			addCell(newRow, cats[t][0]);
			addCell(newRow, "N/A");
		}
		else {
		newRow = table.insertRow();
		addCell(newRow, cats[t][0]);
		addCell(newRow, cats[t][1]);
		}
		var x = document.getElementById("categories");
		var option = document.createElement("option");
		option.text = cats[t][0];
		x.add(option);
	}
	makeRequest("GET", "/purchases", 200, repopulatePurchase);
}
// setup load event
window.addEventListener("load", setup, true);

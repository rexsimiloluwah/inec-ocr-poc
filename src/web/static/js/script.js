const fileUploadInput = document.getElementById("uploadImage");
const fileUploadButton = document.querySelector(".upload-image__button");
const processImageButton = document.querySelector(".process-image__button");
const resultsPlaceholder = document.querySelector(".results__placeholder");
const resultsWrapper = document.querySelector(".results__wrapper");
const emptyResultsWrapperContent = resultsWrapper.innerHTML;

fileUploadInput.addEventListener("change", function(e){
    const uploadedFile = e.target.value;
    if(uploadedFile){
        processImageButton.style.display = "block";
        fileUploadButton.style.fontWeight = 500;
        fileUploadButton.style.fontSize = '16px';
        const fileName = uploadedFile.replace("C:\\fakepath\\","");
        fileUploadButton.querySelector("span").innerHTML = `${fileName.slice(0, 40)} ${fileName.length>40 ? '...' : ''}`;
    }
})

processImageButton.addEventListener("click", function(){
    // Clear the results container 
    resultsWrapper.innerHTML = emptyResultsWrapperContent;

    this.querySelector(".text").innerHTML = "Processing image";
    this.querySelector("#loader").style.display = "inline-block";
    this.classList.add("disabled")

    // Fetch the uploaded file
    const uploadedFile = fileUploadInput.files[0]

    if(uploadedFile){
        const formData = new FormData()
        formData.append("file", uploadedFile)

        // for (pair of formData.entries()){
        //     console.log(pair[0], pair[1])
        // }

        // Send the request to the server
        let xhr = new XMLHttpRequest()
        xhr.open("POST", "/inec-ocr", true);

        // Set the request header
        // xhr.setRequestHeader("Content-Type", "multipart/form-data");

        xhr.onreadystatechange = function(){
            if (this.readyState === XMLHttpRequest.DONE){
                processImageButton.querySelector(".text").innerHTML = "Process Image";
                processImageButton.querySelector("#loader").style.display = "none";
                processImageButton.classList.remove("disabled");
                resultsPlaceholder.style.display = "none";
            }
        }

        xhr.onload = function() { 
            const response = JSON.parse(this.responseText) 

            // Render the results 
            if(response.status){
                resultsWrapper.innerHTML = emptyResultsWrapperContent;
                resultsWrapper.style.visibility = "visible";

                const annotatedImageContainer = resultsWrapper.querySelector(".annotated-img__container");
                const resultsDataContainer = resultsWrapper.querySelector(".results-data__container");

                // Render the annotated image
                const annotatedImg = document.createElement("img");
                annotatedImg.src = response.data.output_image_url;
                annotatedImg.alt = "OCR Annotated Image";
                annotatedImageContainer.prepend(annotatedImg);

                const politicalPartiesResultsResponse = response.data.political_parties_vote_results;
                const puDataResponse = response.data.pu_data_results;
                const puRegInfoResponse = response.data.pu_reg_info_results;
                const electionType = response.data.election_type;

                // Render the election type
                if(electionType){
                    const electionTypeCard = createResultsCard("Election Type", electionType)
                    resultsDataContainer.appendChild(electionTypeCard)
                }else{
                    const electionTypeErrorCard = createErrorCard("Ooops! Failed to extract the election type.")
                    resultsDataContainer.appendChild(electionTypeErrorCard)
                }

                // Render the PU reg info table
                if(puRegInfoResponse){
                    const puRegInfoResults = Object.keys(puRegInfoResponse).map(key => {
                        return {key: key, value: puRegInfoResponse[key]||"-"}
                    })
     
                    const puRegInfoTable = createKeyValueTableCard(
                        "Polling Unit Registration Info",
                        ["Name", "Value"],
                        puRegInfoResults
                    )
                    
                    resultsDataContainer.appendChild(puRegInfoTable);
                }else{
                    const puRegInfoResponseErrorCard = createErrorCard("Ooops! Failed to extract the polling unit registration info.")
                    resultsDataContainer.appendChild(puRegInfoResponseErrorCard)
                }

                // Render the vote results table
                if(politicalPartiesResultsResponse){
                    const politicalPartiesResultsData = Object.keys(politicalPartiesResultsResponse).map((key) => {
                        return {key: key, value: politicalPartiesResultsResponse[key]||"-"}
                    })

                    const politicalPartiesResultsTable = createKeyValueTableCard(
                        "Voting Results",
                        ["Party", "No. of Votes"],
                        politicalPartiesResultsData
                    );

                    resultsDataContainer.appendChild(politicalPartiesResultsTable);
                }else{
                    const politicalPartiesResponseErrorCard = createErrorCard("Ooops! Failed to extract the political parties result.")
                    resultsDataContainer.appendChild(politicalPartiesResponseErrorCard)
                }

                // Render the PU data information
                if(puDataResponse){
                    const puDataResults = Object.keys(puDataResponse).map(key => {
                        return {key: key, value: puDataResponse[key]||"-"}
                    })
     
                    const puDataTable = createKeyValueTableCard(
                        "Polling Unit Data",
                        ["Name", "Count"],
                        puDataResults
                    )
                    
                    resultsDataContainer.appendChild(puDataTable);
                }else{
                    const puDataResponseErrorCard = createErrorCard("Ooops! Failed to extract the polling unit data from the image.")
                    resultsDataContainer.appendChild(puDataResponseErrorCard)
                }

                
                // Scroll to the results container view
                scrollIntoView("results__container")
            }
        }
    xhr.send(formData)
    } 
    }
)

/**
 * Create a table for rendering the response data 
 * @param {*} tableHeaders 
 * @param {*} data 
 * @returns 
 */
const createKeyValueTable = (tableHeaders, data) => {
    // Create a table element
    const table = document.createElement('table');
    
    // Set table styles
    table.style.borderCollapse = 'collapse';
    table.style.border = '2px solid darkgray';
    
    // Create table header
    const tableHeader = document.createElement("thead");
    // Create table header row
    const tableHeaderRow = document.createElement('tr');

    const snEl = document.createElement("th");
    snEl.textContent = "S/N";
    tableHeaderRow.appendChild(snEl);
    
    // Create the column headers
    for (headerName of tableHeaders){
        const headerEl = document.createElement("th");
        headerEl.textContent = headerName;
        tableHeaderRow.appendChild(headerEl)
    }

    // Add the header to the table 
    tableHeader.appendChild(tableHeaderRow)
    table.appendChild(tableHeader);

    // Create table body
    const tableBody = document.createElement("tbody");

    // Create the table data rows 
    for (let i=0; i<data.length; i++){
        const rowData = data[i];

        // Create the table row element 
        const rowEl = document.createElement("tr");

        // Create the S/N cell 
        const snCell = document.createElement("td");
        snCell.textContent = i+1;

        // Create the key cell
        const keyCell = document.createElement("td");
        keyCell.textContent = rowData.key;

        // Create the value cell 
        const valueCell = document.createElement("td");
        valueCell.textContent = rowData.value;

        // Append the cells to the row
        rowEl.appendChild(snCell);
        rowEl.appendChild(keyCell);
        rowEl.appendChild(valueCell);

        // Append the row to the table body
        tableBody.appendChild(rowEl);
    }

    table.appendChild(tableBody)

    return table;
}


/**
 * Create a card for rendering the results data
 * @param {*} title
 * @param {*} body
 * @returns
 */
const createResultsCard = (title, body) => {
    // Create the card div 
    const resultsCard = document.createElement('div');
    resultsCard.className = "results__card";

    const resultsCardHeader = document.createElement('div');
    const resultsCardBody = document.createElement('div');

    resultsCardHeader.className = "results__card--header";
    resultsCardBody.className = "results__card--body";

    resultsCardHeader.innerHTML = `<h3>${title}</h3>`;
    
    if(typeof(body) != "object"){
        const bodyEl = document.createElement("div");
        bodyEl.innerHTML = body;
        resultsCardBody.appendChild(bodyEl)
    }else{
        resultsCardBody.appendChild(body)
    }
    
    resultsCard.appendChild(resultsCardHeader);
    resultsCard.appendChild(resultsCardBody);

    return resultsCard;
}

/**
 * Create a card for rendering the key-value table from the response data
 * @param {*} title
 * @param {*} tableHeaders
 * @param {*} data 
 * @returns 
 */
const createKeyValueTableCard = (title, tableHeaders, data) => {
    const table = createKeyValueTable(tableHeaders, data)
    const resultsCard = createResultsCard(title, table)
    return resultsCard
}

/**
 * Create an error card
 * @param {*} error
 * @returns
 */
const createErrorCard = (error) => {
    const cardEl = document.createElement("div");
    cardEl.className = "error__card";
    cardEl.textContent = error;
    return cardEl;
}

/**
 * Scroll into the view of a particular element
 * @param {*} elementId 
 */
const scrollIntoView = (elementId) => {
    const element = document.getElementById(elementId);

    if(element){
        element.scrollIntoView({behavior: "smooth"})
    }
}

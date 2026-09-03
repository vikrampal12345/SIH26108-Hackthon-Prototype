// Connect the Syncronal frontend to the FastAPI text and document recommendation APIs.

const API_URL = "http://127.0.0.1:8000";


const textTab = document.getElementById("textTab");
const uploadTab = document.getElementById("uploadTab");

const textInputPanel =
    document.getElementById("textInputPanel");

const uploadPanel =
    document.getElementById("uploadPanel");

const queryInput =
    document.getElementById("queryInput");

const searchButton =
    document.getElementById("searchButton");

const documentInput =
    document.getElementById("documentInput");

const dropZone =
    document.getElementById("dropZone");

const selectedFile =
    document.getElementById("selectedFile");

const selectedFileName =
    document.getElementById("selectedFileName");

const removeFileButton =
    document.getElementById("removeFileButton");

const uploadButton =
    document.getElementById("uploadButton");

const statusSection =
    document.getElementById("statusSection");

const statusTitle =
    document.getElementById("statusTitle");

const statusMessage =
    document.getElementById("statusMessage");

const errorSection =
    document.getElementById("errorSection");

const errorMessage =
    document.getElementById("errorMessage");

const resultsSection =
    document.getElementById("resultsSection");

const resultsContainer =
    document.getElementById("resultsContainer");

const candidateCount =
    document.getElementById("candidateCount");

const recommendationCount =
    document.getElementById("recommendationCount");

const resultSource =
    document.getElementById("resultSource");


let selectedDocument = null;


/* ---------- SECURITY ---------- */

function escapeHTML(value) {
    // Safely escape backend data before inserting it into the webpage.
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function safeURL(url) {
    // Allow only HTTPS links hosted on the official BIS standards domain.
    try {

        if (!url) {
            return "#";
        }

        const parsedURL = new URL(url);

        if (
            parsedURL.protocol === "https:" &&
            parsedURL.hostname === "standards.bis.gov.in"
        ) {
            return parsedURL.href;
        }

        return "#";

    } catch (error) {
        return "#";
    }
}


/* ---------- HELPERS ---------- */

function formatScore(score) {
    // Convert a model score into a readable percentage.
    const numericScore = Number(score);

    if (!Number.isFinite(numericScore)) {
        return "0%";
    }

    const percentage =
        Math.max(
            0,
            Math.min(100, numericScore * 100)
        );

    return `${percentage.toFixed(1)}%`;
}


function formatFileSize(bytes) {
    // Convert bytes into a readable file size.
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


/* ---------- TABS ---------- */

function showTextPanel() {
    // Display manual input mode and hide document upload mode.
    textTab.classList.add("active");
    uploadTab.classList.remove("active");

    textInputPanel.classList.remove("hidden");
    uploadPanel.classList.add("hidden");
}


function showUploadPanel() {
    // Display document upload mode and hide manual input mode.
    uploadTab.classList.add("active");
    textTab.classList.remove("active");

    uploadPanel.classList.remove("hidden");
    textInputPanel.classList.add("hidden");
}


textTab.addEventListener(
    "click",
    showTextPanel
);


uploadTab.addEventListener(
    "click",
    showUploadPanel
);


/* ---------- EXAMPLES ---------- */

document
    .querySelectorAll(".example-button")
    .forEach((button) => {

        // Put a predefined procurement requirement into the text box.
        button.addEventListener(
            "click",
            () => {

                queryInput.value =
                    button.dataset.query;

                showTextPanel();

                queryInput.focus();
            }
        );

    });


/* ---------- STATUS ---------- */

function setLoading(title, message) {
    // Show the processing state while Syncronal analyzes the input.
    statusTitle.textContent = title;

    statusMessage.textContent = message;

    statusSection.classList.remove(
        "hidden"
    );

    errorSection.classList.add(
        "hidden"
    );

    resultsSection.classList.add(
        "hidden"
    );
}


function hideLoading() {
    // Hide the processing state after analysis is complete.
    statusSection.classList.add(
        "hidden"
    );
}


function showError(message) {
    // Show a user-readable validation or API error.
    hideLoading();

    errorMessage.textContent =
        message ||
        "An unexpected error occurred.";

    errorSection.classList.remove(
        "hidden"
    );

    resultsSection.classList.add(
        "hidden"
    );
}


/* ---------- DETAILS ---------- */

function createDetailRow(label, value) {
    // Create one metadata row for a BIS recommendation.
    return `
        <div class="detail-row">

            <span class="detail-label">
                ${escapeHTML(label)}
            </span>

            <span class="detail-value">
                ${escapeHTML(
                    value || "Not Available"
                )}
            </span>

        </div>
    `;
}


/* ---------- REFERRED / RELATED ---------- */

function createRelatedStandards(relatedStandards) {
    // Render BIS referral relationships while keeping them separate from recommendations.

    if (
        !Array.isArray(relatedStandards) ||
        relatedStandards.length === 0
    ) {

        return `
            <div class="related-section">

                <h4>
                    Referred / Related Standards
                </h4>

                <p class="empty-related">
                    No referred or related standards found.
                </p>

            </div>
        `;
    }


    const items =
        relatedStandards
            .map((related) => {

                const relationship =
                    related.relationship_type ||
                    related.direction ||
                    "Relationship unavailable";


                let relationshipLabel =
                    relationship;


                if (
                    relationship ===
                    "REFERRED_IN_STANDARD"
                ) {

                    relationshipLabel =
                        "Referred In";

                } else if (
                    relationship ===
                    "REFERRED_BY_STANDARD"
                ) {

                    relationshipLabel =
                        "Referred By";
                }


                return `
                    <div class="related-item">

                        <div class="related-standard-main">

                            <a
                                class="related-number"
                                href="${safeURL(
                                    related.source_url
                                )}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                ${escapeHTML(
                                    related.is_number
                                )}
                            </a>

                            <div class="related-title">
                                ${escapeHTML(
                                    related.title ||
                                    "Title unavailable"
                                )}
                            </div>

                        </div>


                        <div class="related-meta">

                            <span class="related-status">
                                ${escapeHTML(
                                    related.status ||
                                    "Unknown"
                                )}
                            </span>

                            <span class="relationship-type">
                                ${escapeHTML(
                                    relationshipLabel
                                )}
                            </span>

                        </div>

                    </div>
                `;
            })
            .join("");


    return `
        <div class="related-section">

            <h4>
                Referred / Related Standards
            </h4>

            <div class="related-list">
                ${items}
            </div>

        </div>
    `;
}


/* ---------- RECOMMENDATION CARD ---------- */

function createRecommendationCard(recommendation) {
    // Build a complete recommendation card from the FastAPI response.
    const detailsId =
        `details-${recommendation.rank}`;


    const relatedStandards =
        recommendation.related_standards || [];


    return `
        <article class="recommendation-card">

            <div class="recommendation-top">

                <div class="rank-badge">
                    #${recommendation.rank}
                </div>


                <div class="standard-heading">

                    <span class="standard-number">
                        ${escapeHTML(
                            recommendation.is_number
                        )}
                    </span>

                    <h3>
                        ${escapeHTML(
                            recommendation.title
                        )}
                    </h3>

                </div>


                <div class="match-score">

                    <strong>
                        ${formatScore(
                            recommendation.hybrid_score
                        )}
                    </strong>

                    <span>
                        Match
                    </span>

                </div>

            </div>


            <div class="recommendation-badges">

                <span class="status-badge">
                    ${escapeHTML(
                        recommendation.status
                    )}
                </span>

                <span class="certification-badge">
                    ${escapeHTML(
                        recommendation.certification
                    )}
                </span>

                <span class="type-badge">
                    ${escapeHTML(
                        recommendation.type_of_standard
                    )}
                </span>

            </div>


            <div class="score-summary">

                <div class="score-item">

                    <span>
                        Semantic Similarity
                    </span>

                    <strong>
                        ${formatScore(
                            recommendation.semantic_score
                        )}
                    </strong>

                </div>


                <div class="score-item">

                    <span>
                        Classification
                    </span>

                    <strong>
                        ${formatScore(
                            recommendation.classification_score
                        )}
                    </strong>

                </div>

            </div>


            <div class="card-actions">

                <a
                    class="bis-link"
                    href="${safeURL(
                        recommendation.source_url
                    )}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Official BIS
                </a>


                <button
                    type="button"
                    class="details-button"
                    data-target="${detailsId}"
                >
                    View all details
                </button>

            </div>


            <div
                id="${detailsId}"
                class="details-section hidden"
            >

                <div class="details-grid">

                    ${createDetailRow(
                        "Department",
                        recommendation.department
                    )}

                    ${createDetailRow(
                        "Technical Committee",
                        recommendation.technical_committee
                    )}

                    ${createDetailRow(
                        "Group",
                        recommendation.group
                    )}

                    ${createDetailRow(
                        "Sub Group",
                        recommendation.sub_group
                    )}

                    ${createDetailRow(
                        "Sub-Sub Group",
                        recommendation.sub_sub_group
                    )}

                    ${createDetailRow(
                        "Type of Standard",
                        recommendation.type_of_standard
                    )}

                    ${createDetailRow(
                        "Reviewed In",
                        recommendation.reviewed_in
                    )}

                    ${createDetailRow(
                        "Number of Revisions",
                        recommendation.number_of_revisions
                    )}

                    ${createDetailRow(
                        "Number of Amendments",
                        recommendation.number_of_amendments
                    )}

                    ${createDetailRow(
                        "Reaffirmation Year",
                        recommendation.reaffirmation_year
                    )}

                    ${createDetailRow(
                        "Superseding IS",
                        recommendation.superseding_is
                    )}

                    ${createDetailRow(
                        "Relevant Ministries",
                        recommendation.relevant_ministries
                    )}

                    ${createDetailRow(
                        "Common-Man Title",
                        recommendation.short_common_man_title
                    )}

                    ${createDetailRow(
                        "Certification",
                        recommendation.certification
                    )}

                    ${createDetailRow(
                        "Hybrid Score",
                        formatScore(
                            recommendation.hybrid_score
                        )
                    )}

                </div>


                ${createRelatedStandards(
                    relatedStandards
                )}

            </div>

        </article>
    `;
}


/* ---------- RENDER RESULTS ---------- */

function renderResults(data) {
    // Render the recommendation results returned by either API endpoint.

    candidateCount.textContent =
        data.candidates_retrieved ?? 0;


    recommendationCount.textContent =
        data.recommendation_count ?? 0;


    if (
        data.input_type ===
        "document"
    ) {

        resultSource.textContent =
            `Analyzed document: ${
                data.filename ||
                "Uploaded file"
            } • ${
                data.extracted_text_length ||
                0
            } characters extracted`;

    } else {

        resultSource.textContent =
            `Analyzed requirement: "${
                data.query
            }"`;
    }


    if (
        !Array.isArray(
            data.recommendations
        ) ||
        data.recommendations.length === 0
    ) {

        resultsContainer.innerHTML = `
            <div class="empty-results">
                No suitable BIS standards were found.
            </div>
        `;

        resultsSection.classList.remove(
            "hidden"
        );

        return;
    }


    resultsContainer.innerHTML =
        data.recommendations
            .map(
                createRecommendationCard
            )
            .join("");


    resultsSection.classList.remove(
        "hidden"
    );


    document
        .querySelectorAll(
            ".details-button"
        )
        .forEach((button) => {

            // Toggle complete metadata and referred standards for each card.
            button.addEventListener(
                "click",
                () => {

                    const targetId =
                        button.dataset.target;

                    const target =
                        document.getElementById(
                            targetId
                        );

                    if (!target) {
                        return;
                    }


                    const isHidden =
                        target.classList.contains(
                            "hidden"
                        );


                    target.classList.toggle(
                        "hidden"
                    );


                    button.textContent =
                        isHidden
                            ? "Hide details"
                            : "View all details";
                }
            );

        });
}


/* ---------- TEXT RECOMMENDATION ---------- */

async function recommendFromText() {
    // Send the manually entered procurement requirement to FastAPI.

    const query =
        queryInput.value.trim();


    if (query.length < 3) {

        showError(
            "Please enter at least 3 characters."
        );

        return;
    }


    setLoading(
        "Analyzing requirement...",
        "Finding relevant BIS standards."
    );


    searchButton.disabled = true;


    try {

        const response =
            await fetch(
                `${API_URL}/recommend`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        query: query
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Recommendation request failed."
            );
        }


        hideLoading();

        renderResults(data);

    } catch (error) {

        showError(
            error.message ||
            "Unable to connect to the backend."
        );

    } finally {

        searchButton.disabled = false;
    }
}


/* ---------- DOCUMENT RECOMMENDATION ---------- */

async function recommendFromDocument() {
    // Upload the selected file to FastAPI and request BIS recommendations.

    if (!selectedDocument) {

        showError(
            "Please select a PDF, DOCX or TXT file."
        );

        return;
    }


    const extension =
        `.${selectedDocument.name
            .split(".")
            .pop()
            .toLowerCase()}`;


    if (
        ![
            ".pdf",
            ".docx",
            ".txt"
        ].includes(extension)
    ) {

        showError(
            "Unsupported file type. Upload PDF, DOCX or TXT."
        );

        return;
    }


    if (
        selectedDocument.size >
        10 * 1024 * 1024
    ) {

        showError(
            "File is too large. Maximum size is 10 MB."
        );

        return;
    }


    setLoading(
        "Analyzing document...",
        "Extracting requirements and finding relevant BIS standards."
    );


    uploadButton.disabled = true;


    try {

        const formData =
            new FormData();


        formData.append(
            "file",
            selectedDocument
        );


        const response =
            await fetch(
                `${API_URL}/recommend-document`,
                {
                    method: "POST",

                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Document analysis failed."
            );
        }


        hideLoading();

        renderResults(data);

    } catch (error) {

        showError(
            error.message ||
            "Unable to analyze the document."
        );

    } finally {

        uploadButton.disabled = false;
    }
}


/* ---------- BUTTON EVENTS ---------- */

searchButton.addEventListener(
    "click",
    recommendFromText
);


uploadButton.addEventListener(
    "click",
    recommendFromDocument
);


/* ---------- KEYBOARD ---------- */

queryInput.addEventListener(
    "keydown",
    (event) => {

        // Allow Ctrl+Enter to submit the procurement requirement.
        if (
            event.key === "Enter" &&
            event.ctrlKey
        ) {

            recommendFromText();
        }
    }
);


/* ---------- FILE SELECTION ---------- */

documentInput.addEventListener(
    "change",
    () => {

        // Store the selected document and update the upload interface.

        const file =
            documentInput.files?.[0];


        if (!file) {
            return;
        }


        setSelectedDocument(file);
    }
);


function setSelectedDocument(file) {
    // Validate and store a selected or dropped document.

    const extension =
        `.${file.name
            .split(".")
            .pop()
            .toLowerCase()}`;


    if (
        ![
            ".pdf",
            ".docx",
            ".txt"
        ].includes(extension)
    ) {

        showError(
            "Unsupported file type. Upload PDF, DOCX or TXT."
        );

        return;
    }


    if (
        file.size >
        10 * 1024 * 1024
    ) {

        showError(
            "File is too large. Maximum size is 10 MB."
        );

        return;
    }


    selectedDocument = file;


    selectedFileName.textContent =
        `${file.name} (${formatFileSize(
            file.size
        )})`;


    selectedFile.classList.remove(
        "hidden"
    );


    uploadButton.disabled = false;


    errorSection.classList.add(
        "hidden"
    );
}


/* ---------- REMOVE FILE ---------- */

removeFileButton.addEventListener(
    "click",
    () => {

        // Remove the selected document and reset the upload controls.

        selectedDocument = null;

        documentInput.value = "";

        selectedFile.classList.add(
            "hidden"
        );

        uploadButton.disabled = true;
    }
);


/* ---------- DRAG AND DROP ---------- */

dropZone.addEventListener(
    "dragover",
    (event) => {

        // Allow a document to be dragged over the upload area.

        event.preventDefault();

        dropZone.classList.add(
            "drag-over"
        );
    }
);


dropZone.addEventListener(
    "dragleave",
    () => {

        // Remove the drag-over visual effect.

        dropZone.classList.remove(
            "drag-over"
        );
    }
);


dropZone.addEventListener(
    "drop",
    (event) => {

        // Accept a dropped document and pass it through validation.

        event.preventDefault();

        dropZone.classList.remove(
            "drag-over"
        );


        const file =
            event.dataTransfer.files?.[0];


        if (!file) {
            return;
        }


        setSelectedDocument(file);
    }
);
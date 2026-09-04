// Connect the Syncronal frontend to FastAPI with proper text and document validation errors.

const API_URL = "http://127.0.0.1:8000";


// ---------- DOM ELEMENTS ----------

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


// ---------- SECURITY ----------

function escapeHTML(value) {
    // Safely escape values before inserting them into the page.
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function safeURL(url) {
    // Allow only official BIS HTTPS URLs.
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

    } catch {
        return "#";
    }
}


// ---------- API ERROR ----------

async function getApiErrorMessage(
    response,
    fallbackMessage,
) {
    // Extract the actual FastAPI error message returned by the backend.
    try {
        const contentType =
            response.headers.get("content-type") || "";

        if (
            contentType.includes(
                "application/json"
            )
        ) {
            const data =
                await response.json();

            if (
                typeof data.detail ===
                "string"
            ) {
                return data.detail;
            }

            if (
                Array.isArray(data.detail)
            ) {
                const messages =
                    data.detail
                        .map(
                            (item) =>
                                item?.msg
                        )
                        .filter(Boolean);

                if (
                    messages.length > 0
                ) {
                    return messages.join(
                        " "
                    );
                }
            }
        }

        const text =
            await response.text();

        if (text.trim()) {
            return text.trim();
        }

    } catch {
        // Use the fallback when the response cannot be parsed.
    }

    return fallbackMessage;
}


// ---------- HELPERS ----------

function formatScore(score) {
    // Convert a model score into a readable percentage.
    const numericScore =
        Number(score);

    if (
        !Number.isFinite(
            numericScore
        )
    ) {
        return "0%";
    }

    const percentage =
        Math.max(
            0,
            Math.min(
                100,
                numericScore * 100
            )
        );

    return `${percentage.toFixed(1)}%`;
}


function formatFileSize(bytes) {
    // Convert file size into KB or MB.
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (
        bytes <
        1024 * 1024
    ) {
        return `${(
            bytes / 1024
        ).toFixed(1)} KB`;
    }

    return `${(
        bytes /
        (1024 * 1024)
    ).toFixed(1)} MB`;
}


// ---------- ERROR UI ----------

function clearError() {
    // Hide any previous error message.
    errorSection.classList.add(
        "hidden"
    );
}


function showError(message) {
    // Display the actual validation/API error to the user.
    hideLoading();

    errorMessage.textContent =
        message ||
        "Something went wrong. Please try again.";

    errorSection.classList.remove(
        "hidden"
    );

    resultsSection.classList.add(
        "hidden"
    );

    errorSection.scrollIntoView({
        behavior: "smooth",
        block: "center",
    });
}


// ---------- LOADING UI ----------

function setLoading(
    title,
    message,
) {
    // Show the analysis state while the backend is processing.
    statusTitle.textContent =
        title;

    statusMessage.textContent =
        message;

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
    // Hide the analysis state.
    statusSection.classList.add(
        "hidden"
    );
}


// ---------- TABS ----------

function showTextPanel() {
    // Switch to manual requirement input.
    textTab.classList.add(
        "active"
    );

    uploadTab.classList.remove(
        "active"
    );

    textInputPanel.classList.remove(
        "hidden"
    );

    uploadPanel.classList.add(
        "hidden"
    );
}


function showUploadPanel() {
    // Switch to document upload mode.
    uploadTab.classList.add(
        "active"
    );

    textTab.classList.remove(
        "active"
    );

    uploadPanel.classList.remove(
        "hidden"
    );

    textInputPanel.classList.add(
        "hidden"
    );
}


textTab.addEventListener(
    "click",
    showTextPanel
);

uploadTab.addEventListener(
    "click",
    showUploadPanel
);


// ---------- EXAMPLE BUTTONS ----------

document
    .querySelectorAll(
        ".example-button"
    )
    .forEach((button) => {
        // Fill the requirement box from an example button.
        button.addEventListener(
            "click",
            () => {
                queryInput.value =
                    button.dataset.query;

                showTextPanel();
                clearError();

                queryInput.focus();
            }
        );
    });


// ---------- DETAILS ----------

function createDetailRow(
    label,
    value,
) {
    // Create one recommendation metadata row.
    return `
        <div class="detail-row">

            <span class="detail-label">
                ${escapeHTML(label)}
            </span>

            <span class="detail-value">
                ${escapeHTML(
                    value ||
                    "Not Available"
                )}
            </span>

        </div>
    `;
}


// ---------- RELATED STANDARDS ----------

function createRelatedStandards(
    relatedStandards,
) {
    // Render referred and related BIS standards.
    if (
        !Array.isArray(
            relatedStandards
        ) ||
        relatedStandards.length ===
            0
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


                let label =
                    relationship;


                if (
                    relationship ===
                    "REFERRED_IN_STANDARD"
                ) {
                    label =
                        "Referred In";
                }


                if (
                    relationship ===
                    "REFERRED_BY_STANDARD"
                ) {
                    label =
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
                                ${escapeHTML(label)}
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


// ---------- RECOMMENDATION CARD ----------

function createRecommendationCard(
    recommendation,
) {
    // Build one complete BIS recommendation card.
    const detailsId =
        `details-${recommendation.rank}`;

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
                    recommendation.related_standards ||
                    []
                )}

            </div>

        </article>
    `;
}


// ---------- RENDER RESULTS ----------

function renderResults(data) {
    // Render successful BIS recommendation results.
    candidateCount.textContent =
        data.candidates_retrieved ??
        0;

    recommendationCount.textContent =
        data.recommendation_count ??
        0;


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
        data.recommendations.length ===
            0
    ) {
        resultsContainer.innerHTML =
            `
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
            // Toggle complete recommendation details.
            button.addEventListener(
                "click",
                () => {

                    const target =
                        document.getElementById(
                            button.dataset.target
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


// ---------- TEXT RECOMMENDATION ----------

async function recommendFromText() {
    // Send manual procurement text to FastAPI.
    const query =
        queryInput.value.trim();


    clearError();


    if (query.length < 3) {
        showError(
            "Please enter at least 3 characters."
        );

        return;
    }


    setLoading(
        "Analyzing requirement...",
        "Checking the requirement and finding relevant BIS standards."
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
                            "application/json",
                    },

                    body:
                        JSON.stringify({
                            query: query,
                        }),
                }
            );


        if (!response.ok) {
            // Show the real backend validation error.
            const message =
                await getApiErrorMessage(
                    response,
                    "Recommendation request failed."
                );

            showError(message);

            return;
        }


        const data =
            await response.json();


        hideLoading();

        renderResults(data);

    } catch (error) {

        showError(
            error?.message ||
            "Unable to connect to the backend."
        );

    } finally {

        searchButton.disabled =
            false;
    }
}


// ---------- DOCUMENT RECOMMENDATION ----------

async function recommendFromDocument() {
    // Upload a document and show the backend validation result.
    clearError();


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
            ".txt",
        ].includes(extension)
    ) {
        showError(
            "Unsupported file type. Please upload PDF, DOCX or TXT."
        );

        return;
    }


    if (
        selectedDocument.size >
        10 * 1024 * 1024
    ) {
        showError(
            "File is too large. Maximum allowed size is 10 MB."
        );

        return;
    }


    setLoading(
        "Checking document...",
        "Extracting the document and validating whether it is a BIS procurement requirement."
    );


    uploadButton.disabled =
        true;


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
                    body: formData,
                }
            );


        if (!response.ok) {
            // Show the actual document validation error from FastAPI.
            const message =
                await getApiErrorMessage(
                    response,
                    "Document validation failed."
                );

            showError(message);

            return;
        }


        const data =
            await response.json();


        hideLoading();

        renderResults(data);

    } catch (error) {

        showError(
            error?.message ||
            "Unable to analyze the document."
        );

    } finally {

        uploadButton.disabled =
            false;
    }
}


// ---------- BUTTON EVENTS ----------

searchButton.addEventListener(
    "click",
    recommendFromText
);


uploadButton.addEventListener(
    "click",
    recommendFromDocument
);


// ---------- KEYBOARD ----------

queryInput.addEventListener(
    "keydown",
    (event) => {
        // Allow Ctrl+Enter to submit manual text.
        if (
            event.key === "Enter" &&
            event.ctrlKey
        ) {
            event.preventDefault();

            recommendFromText();
        }
    }
);


// ---------- FILE SELECTION ----------

documentInput.addEventListener(
    "change",
    () => {
        // Validate and store a newly selected file.
        const file =
            documentInput.files?.[0];

        if (!file) {
            return;
        }

        setSelectedDocument(file);
    }
);


function setSelectedDocument(file) {
    // Validate file extension and size before enabling upload.
    const extension =
        `.${file.name
            .split(".")
            .pop()
            .toLowerCase()}`;


    const allowedExtensions =
        [
            ".pdf",
            ".docx",
            ".txt",
        ];


    if (
        !allowedExtensions.includes(
            extension
        )
    ) {

        selectedDocument = null;

        documentInput.value = "";

        selectedFile.classList.add(
            "hidden"
        );

        uploadButton.disabled =
            true;

        showError(
            "Unsupported file type. Please upload PDF, DOCX or TXT."
        );

        return;
    }


    if (
        file.size >
        10 * 1024 * 1024
    ) {

        selectedDocument = null;

        documentInput.value = "";

        selectedFile.classList.add(
            "hidden"
        );

        uploadButton.disabled =
            true;

        showError(
            "File is too large. Maximum allowed size is 10 MB."
        );

        return;
    }


    selectedDocument =
        file;


    selectedFileName.textContent =
        `${file.name} (${formatFileSize(
            file.size
        )})`;


    selectedFile.classList.remove(
        "hidden"
    );


    uploadButton.disabled =
        false;


    clearError();
}


// ---------- REMOVE FILE ----------

removeFileButton.addEventListener(
    "click",
    () => {
        // Remove the selected file and reset the upload UI.
        selectedDocument =
            null;

        documentInput.value =
            "";

        selectedFile.classList.add(
            "hidden"
        );

        uploadButton.disabled =
            true;

        clearError();
    }
);


// ---------- DRAG AND DROP ----------

dropZone.addEventListener(
    "dragover",
    (event) => {
        // Allow files to be dragged over the upload area.
        event.preventDefault();

        dropZone.classList.add(
            "drag-over"
        );
    }
);


dropZone.addEventListener(
    "dragleave",
    () => {
        // Remove the drag-over state.
        dropZone.classList.remove(
            "drag-over"
        );
    }
);


dropZone.addEventListener(
    "drop",
    (event) => {
        // Validate and store the dropped file.
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
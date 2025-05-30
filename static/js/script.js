// Store all selected images for each report type
let selectedImages = {
    college: {
        project: [],
        code: []
    },
    school: {
        project: []
    }
};

// Store selected logos for each report type
let selectedLogos = {
    college: [],
    school: []
};

// Store sections for each report type
let customSections = {
    college: [],
    school: []
};

let predefinedSections = {
    college: [],
    school: []
};

// Initialize Sortable for both report types
document.addEventListener('DOMContentLoaded', function() {
    new Sortable(document.getElementById("college_sortable"), {
        animation: 150,
        ghostClass: 'sortable-ghost',
        onEnd: function() {
            updateOrderedSections('college');
            updateImageUploadVisibility('college');
        }
    });


    new Sortable(document.getElementById("school_sortable"), {
        animation: 150,
        ghostClass: 'sortable-ghost',
        onEnd: function() {
            updateOrderedSections('school');
            updateImageUploadVisibility('school');
        }
    });

    // Initialize with empty sections
    resetAllForms();
});

// Function to reset all forms
function resetAllForms() {
    // Reset both forms
    ['college', 'school'].forEach(type => {
        // Clear text inputs
        document.querySelectorAll(`#${type}ReportForm input[type="text"]`).forEach(input => {
            input.value = '';
            input.classList.remove('is-invalid');
        });
        
        // Uncheck all checkboxes
        document.querySelectorAll(`#${type}ReportForm input[type="checkbox"]`).forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // Clear custom sections
        document.getElementById(`${type}_custom_section_input`).value = '';
        document.getElementById(`${type}_custom_sections`).value = '';
        customSections[type] = [];
        
        // Reset predefined sections
        predefinedSections[type] = [];
        
        // Clear sortable list
        const sortableList = document.getElementById(`${type}_sortable`);
        sortableList.innerHTML = '';
        
        // Clear file inputs and previews
        if (type === 'college') {
            document.getElementById('college_project_images').value = '';
            document.getElementById('college_code_screenshots').value = '';
            document.getElementById('college_project_images_preview').innerHTML = '';
            document.getElementById('college_code_preview').innerHTML = '';
            document.getElementById('college_selected_project_images').value = '';
            document.getElementById('college_selected_code_images').value = '';
            document.getElementById('college_generateImagePrompt').value = '';
            document.getElementById('college_generatedImagePreview').style.display = 'none';
            selectedImages.college.project = [];
            selectedImages.college.code = [];
        } else {
            document.getElementById('school_project_images').value = '';
            document.getElementById('school_project_images_preview').innerHTML = '';
            document.getElementById('school_selected_project_images').value = '';
            document.getElementById('school_generateImagePrompt').value = '';
            document.getElementById('school_generatedImagePreview').style.display = 'none';
            selectedImages.school.project = [];
        }
        
        // Clear logo search and selections
        if (type === 'college') {
            document.getElementById('logoSearchQuery').value = '';
            document.getElementById('logoSearchResults').innerHTML = '';
            document.getElementById('selectedLogoContainer').innerHTML = '';
            document.getElementById('selectedLogoPreview').style.display = 'none';
            document.getElementById('collegeLogoUrls').value = '';
            selectedLogos.college = [];
        } else {
            document.getElementById('schoolLogoSearchQuery').value = '';
            document.getElementById('schoolLogoSearchResults').innerHTML = '';
            document.getElementById('selectedSchoolLogoContainer').innerHTML = '';
            document.getElementById('selectedSchoolLogoPreview').style.display = 'none';
            document.getElementById('schoolLogoUrls').value = '';
            selectedLogos.school = [];
        }
        
        // Update visibility
        updateImageUploadVisibility(type);
    });
    
    // Reset the form display to show college form by default
    showReportType('college');
}


function handleImageUpload(input, type, imageType) {
    const previewId = `${type}_${imageType === 'project' ? 'project_images_preview' : 'code_preview'}`;
    const hiddenInputId = `${type}_selected_${imageType === 'project' ? 'project_images' : 'code_images'}`;
    const storageArray = selectedImages[type][imageType];
    
    // Don't clear previous files - just add new ones
    Array.from(input.files).forEach(file => {
        if (file.size > 5 * 1024 * 1024) {
            alert(`File ${file.name} is too large (max 5MB)`);
            return;
        }
        
        // Check if file already exists
        const fileExists = storageArray.some(existingFile =>
            existingFile.name === file.name && existingFile.size === file.size);
        
        if (!fileExists) {
            storageArray.push(file);
        }
    });
    
    updateFilePreview(previewId, storageArray, hiddenInputId);
    input.value = ''; // Reset input to allow re-upload of same files
}

function updateFilePreview(previewId, storageArray, hiddenInputId) {
    const preview = document.getElementById(previewId);
    const hiddenInput = document.getElementById(hiddenInputId);
    
    preview.innerHTML = '';
    
    if (storageArray.length > 0) {
        const fileNames = [];
        
        storageArray.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-preview-item';
            
            const thumbnail = file.type.startsWith('image/') ?
                `<img src="${URL.createObjectURL(file)}" alt="${file.name}">` :
                '<div class="file-icon">📄</div>';
            
            fileItem.innerHTML = `
                <div style="display: flex; align-items: center;">
                    ${thumbnail}
                    <div>
                        <strong>${file.name}</strong>
                        <div class="text-muted">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger remove-file"
                        data-index="${index}">
                    Remove
                </button>
            `;
            
            preview.appendChild(fileItem);
            fileNames.push(file.name);
        });
        
        hiddenInput.value = fileNames.join(',');
        
        document.querySelectorAll(`#${previewId} .remove-file`).forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                storageArray.splice(index, 1);
                updateFilePreview(previewId, storageArray, hiddenInputId);
            });
        });
    } else {
        hiddenInput.value = '';
    }
}

function showReportType(type) {
    // Update buttons
    document.querySelectorAll('.report-type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.report-type-btn[onclick="showReportType('${type}')"]`).classList.add('active');
    
    // Update forms
    document.querySelectorAll('.report-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${type}ReportForm`).classList.add('active');
}

// Section management functions
function togglePredefinedSection(checkbox, type) {
    const sectionName = checkbox.value;
    
    if (checkbox.checked && !predefinedSections[type].includes(sectionName)) {
        predefinedSections[type].push(sectionName);
        addSectionToOrder(sectionName, type);
    } else {
        predefinedSections[type] = predefinedSections[type].filter(s => s !== sectionName);
        removeSectionFromOrder(sectionName, type);
    }
    updateImageUploadVisibility(type);
}

function addCustomSection(type) {
    const input = document.getElementById(`${type}_custom_section_input`);
    const sectionName = input.value.trim();
    
    if (sectionName && !customSections[type].includes(sectionName)) {
        customSections[type].push(sectionName);
        addSectionToOrder(sectionName, type);
        document.getElementById(`${type}_custom_sections`).value = customSections[type].join(",");
        input.value = "";
    }
}


function addSectionToOrder(sectionName, type) {
    const sortableList = document.getElementById(`${type}_sortable`);
    if (!document.querySelector(`#${type}_sortable li[data-value="${sectionName}"]`)) {
        const li = document.createElement("li");
        li.className = "section-item";
        li.dataset.value = sectionName;
        li.innerHTML = `
            ${sectionName}
            <button type="button" class="remove-section" onclick="removeSection(this, '${type}')">×</button>
        `;
        sortableList.appendChild(li);
        updateOrderedSections(type);
        updateImageUploadVisibility(type);
    }
}

function removeSection(button, type) {
    const li = button.closest('li');
    const sectionName = li.dataset.value;
    
    if (customSections[type].includes(sectionName)) {
        customSections[type] = customSections[type].filter(s => s !== sectionName);
        document.getElementById(`${type}_custom_sections`).value = customSections[type].join(",");
    }
    
    if (predefinedSections[type].includes(sectionName)) {
        predefinedSections[type] = predefinedSections[type].filter(s => s !== sectionName);
        const checkbox = document.querySelector(`#${type}ReportForm input[value="${sectionName}"]`);
        if (checkbox) checkbox.checked = false;
    }
    
    li.remove();
    updateOrderedSections(type);
    updateImageUploadVisibility(type);
}

function removeSectionFromOrder(sectionName, type) {
    const item = document.querySelector(`#${type}_sortable li[data-value="${sectionName}"]`);
    if (item) item.remove();
    updateOrderedSections(type);
    updateImageUploadVisibility(type);
}

function updateOrderedSections(type) {
    const sections = Array.from(document.querySelectorAll(`#${type}_sortable .section-item`))
                        .map(item => item.dataset.value);
    document.getElementById(`${type}_ordered_sections`).value = sections.join(",");
}

function updateImageUploadVisibility(type) {
    const order = document.getElementById(`${type}_ordered_sections`).value.split(',');
    
    if (type === 'college') {
        document.getElementById('college_projectImagesContainer').style.display =
            order.includes('Project Images') ? 'block' : 'none';
        document.getElementById('college_codeScreenshotsContainer').style.display =
            order.includes('Code Screenshots') ? 'block' : 'none';
    } else if (type === 'school') {
        document.getElementById('school_projectImagesContainer').style.display =
            order.includes('Project Images') ? 'block' : 'none';
    }
}

// Form validation
document.getElementById('collegeReportForm').addEventListener('submit', function(e) {
    prepareFormSubmission(e, this, 'college');
});

document.getElementById('schoolReportForm').addEventListener('submit', function(e) {
    prepareFormSubmission(e, this, 'school');
});

function prepareFormSubmission(e, form, type) {
    const requiredFields = ['topic', 'submitted_by', 'submitted_to'];
    let isValid = true;
    
    requiredFields.forEach(field => {
        const input = form.elements[field];
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    if (!isValid) {
        e.preventDefault();
        alert('Please fill all required fields!');
        return;
    }

    // Create new file inputs for our stored images
    const createFileInput = (name, files) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.name = name;
        input.multiple = true;
        input.style.display = 'none';
        
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        input.files = dataTransfer.files;
        
        return input;
    };

    if (selectedImages[type].project.length > 0) {
        const projectInput = createFileInput('project_images', selectedImages[type].project);
        form.appendChild(projectInput);
    }

    if (type === 'college' && selectedImages[type].code.length > 0) {
        const codeInput = createFileInput('code_screenshots', selectedImages[type].code);
        form.appendChild(codeInput);
    }
}

// Image generation functions
function generateImage(type) {
    const prompt = document.getElementById(`${type}_generateImagePrompt`).value.trim();
    if (!prompt) {
        alert('Please enter a prompt for image generation');
        return;
    }

    // Show loading state
    const generateBtn = document.querySelector(`#${type}ReportForm button[onclick="generateImage('${type}')"]`);
    const originalText = generateBtn.innerHTML;
    generateBtn.innerHTML = 'Generating...';
    generateBtn.disabled = true;

    fetch('/generate-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt: prompt,
            report_type: type
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const preview = document.getElementById(`${type}_generatedImagePreview`);
            const img = document.getElementById(`${type}_generatedImage`);
            img.src = data.imageUrl;
            preview.style.display = 'block';
        } else {
            alert(data.error || 'Image generation failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to generate image');
    })
    .finally(() => {
        generateBtn.innerHTML = originalText;
        generateBtn.disabled = false;
    });
}

function addGeneratedImageToProject(type) {
    const img = document.getElementById(`${type}_generatedImage`);
    const imgUrl = img.src;
    
    // Convert the image URL to a File object
    fetch(imgUrl)
        .then(response => response.blob())
        .then(blob => {
            const file = new File([blob], `generated-image-${Date.now()}.jpg`, { type: 'image/jpeg' });
            
            // Add to the appropriate storage array
            selectedImages[type].project.push(file);
            
            // Update the preview
            const previewId = `${type}_project_images_preview`;
            const hiddenInputId = `${type}_selected_project_images`;
            updateFilePreview(previewId, selectedImages[type].project, hiddenInputId);
            
            // Hide the generated image preview
            document.getElementById(`${type}_generateImagePrompt`).value = '';
            document.getElementById(`${type}_generatedImagePreview`).style.display = 'none';
        })
        .catch(error => {
            console.error('Error adding generated image:', error);
            alert('Failed to add generated image to project');
        });
}

// Logo search and selection functions
function searchLogo() {
    const query = document.getElementById('logoSearchQuery').value.trim();
    if (!query) {
        alert('Please enter a search term');
        return;
    }

    const resultsContainer = document.getElementById('logoSearchResults');
    resultsContainer.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

    fetch(`/search-logo?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = '';
            
            if (data.items && data.items.length > 0) {
                data.items.slice(0, 6).forEach(item => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4 col-6 mb-3';
                    
                    const imgWrapper = document.createElement('div');
                    imgWrapper.className = 'logo-thumbnail';
                    imgWrapper.onclick = () => selectLogo(item.link, item.image.contextLink, 'college');
                    
                    const img = document.createElement('img');
                    img.src = item.link;
                    img.className = 'img-fluid';
                    img.style.cursor = 'pointer';
                    img.style.maxHeight = '100px';
                    img.onerror = function() { this.style.display = 'none'; };
                    
                    imgWrapper.appendChild(img);
                    col.appendChild(imgWrapper);
                    resultsContainer.appendChild(col);
                });
            } else {
                resultsContainer.innerHTML = '<div class="col-12 text-center">No logos found. Try a different search term.</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<div class="col-12 text-center">Error loading logos. Please try again.</div>';
        });
}


function searchSchoolLogo() {
    const query = document.getElementById('schoolLogoSearchQuery').value.trim();
    if (!query) {
        alert('Please enter a search term');
        return;
    }

    const resultsContainer = document.getElementById('schoolLogoSearchResults');
    resultsContainer.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

    fetch(`/search-logo?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = '';
            
            if (data.items && data.items.length > 0) {
                data.items.slice(0, 6).forEach(item => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4 col-6 mb-3';
                    
                    const imgWrapper = document.createElement('div');
                    imgWrapper.className = 'logo-thumbnail';
                    imgWrapper.onclick = () => selectLogo(item.link, item.image.contextLink, 'school');
                    
                    const img = document.createElement('img');
                    img.src = item.link;
                    img.className = 'img-fluid';
                    img.style.cursor = 'pointer';
                    img.style.maxHeight = '100px';
                    img.onerror = function() { this.style.display = 'none'; };
                    
                    imgWrapper.appendChild(img);
                    col.appendChild(imgWrapper);
                    resultsContainer.appendChild(col);
                });
            } else {
                resultsContainer.innerHTML = '<div class="col-12 text-center">No logos found. Try a different search term.</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<div class="col-12 text-center">Error loading logos. Please try again.</div>';
        });
}

function selectLogo(imageUrl, sourceUrl, type) {
    // Check if logo already exists
    if (!selectedLogos[type].some(logo => logo.url === imageUrl)) {
        selectedLogos[type].push({
            url: imageUrl,
            source: sourceUrl
        });
        updateLogoPreview(type);
    }
}

function updateLogoPreview(type) {
    let container, preview, hiddenInput;
    
    if (type === 'college') {
        container = document.getElementById('selectedLogoContainer');
        preview = document.getElementById('selectedLogoPreview');
        hiddenInput = document.getElementById('collegeLogoUrls');
    } else {
        container = document.getElementById('selectedSchoolLogoContainer');
        preview = document.getElementById('selectedSchoolLogoPreview');
        hiddenInput = document.getElementById('schoolLogoUrls');
    }

    if (!container || !preview || !hiddenInput) {
        console.error('Could not find logo preview elements for type:', type);
        return;
    }

    container.innerHTML = '';
    
    if (selectedLogos[type].length > 0) {
        selectedLogos[type].forEach((logo, index) => {
            const logoDiv = document.createElement('div');
            logoDiv.className = 'logo-preview-item m-2';
            logoDiv.innerHTML = `
                <img src="${logo.url}" class="img-fluid" style="max-height: 80px;">
                <button type="button" class="btn btn-sm btn-danger remove-logo" 
                        data-index="${index}" onclick="removeLogo(${index}, '${type}')">
                    ×
                </button>
            `;
            container.appendChild(logoDiv);
        });
        
        hiddenInput.value = JSON.stringify(selectedLogos[type]);
        preview.style.display = 'block';
    } else {
        hiddenInput.value = '';
        preview.style.display = 'none';
    }
}


function removeLogo(index, type) {
    selectedLogos[type].splice(index, 1);
    updateLogoPreview(type);
}
// // AIzaSyC1tKIThniS8kGBiM6H5Ql8sQ0uB0t97rQ


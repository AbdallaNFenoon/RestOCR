// State management
let menuData = { categories: [] };
let activeCategoryIndex = 0;
let geminiApiKey = localStorage.getItem("gemini_api_key") || "";

// DOM Elements
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const btnBrowse = document.getElementById("btn-browse");
const uploadStatus = document.getElementById("upload-status");
const statusHeading = document.getElementById("status-heading");
const statusDetail = document.getElementById("status-detail");

const uploadView = document.getElementById("upload-view");
const editorView = document.getElementById("editor-view");

const apiPanel = document.getElementById("api-panel");
const apiKeyInput = document.getElementById("api-key-input");
const btnToggleKeyVisibility = document.getElementById("btn-toggle-key-visibility");
const btnApiSettings = document.getElementById("btn-api-settings");
const btnCloseApi = document.getElementById("btn-close-api");
const btnSaveApi = document.getElementById("btn-save-api");
const btnShutdown = document.getElementById("btn-shutdown");

const categoryList = document.getElementById("category-list");
const activeCatTitleEn = document.getElementById("active-cat-title-en");
const activeCatTitleAr = document.getElementById("active-cat-title-ar");
const itemsTableBody = document.getElementById("items-table-body");

const btnAddCategory = document.getElementById("btn-add-category");
const btnEditActiveCat = document.getElementById("btn-edit-active-cat");
const btnDeleteActiveCat = document.getElementById("btn-delete-active-cat");
const btnAddItem = document.getElementById("btn-add-item");
const btnExportExcel = document.getElementById("btn-export-excel");

// Dialogs
const categoryDialog = document.getElementById("category-dialog");
const catDialogTitle = document.getElementById("cat-dialog-title");
const catInputEn = document.getElementById("cat-input-en");
const catInputAr = document.getElementById("cat-input-ar");
const btnCancelCat = document.getElementById("btn-cancel-cat");
const btnSaveCat = document.getElementById("btn-save-cat");
let dialogMode = "add"; // "add" or "edit"

// Initialize API Key fields
if (geminiApiKey) {
    apiKeyInput.value = geminiApiKey;
} else {
    // Proactively show API panel if key is missing
    apiPanel.classList.remove("hidden");
}

// Toast Notification Helper
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let iconClass = "fa-info-circle";
    if (type === "success") iconClass = "fa-check-circle";
    if (type === "danger") iconClass = "fa-exclamation-circle";
    
    toast.innerHTML = `<i class="fa-solid ${iconClass}"></i><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(50px)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// API Key Management
btnApiSettings.addEventListener("click", () => {
    apiPanel.classList.toggle("hidden");
});
btnCloseApi.addEventListener("click", () => {
    apiPanel.classList.add("hidden");
});
btnToggleKeyVisibility.addEventListener("click", () => {
    const type = apiKeyInput.type === "password" ? "text" : "password";
    apiKeyInput.type = type;
    btnToggleKeyVisibility.innerHTML = type === "password" ? 
        '<i class="fa-solid fa-eye"></i>' : 
        '<i class="fa-solid fa-eye-slash"></i>';
});
btnSaveApi.addEventListener("click", () => {
    geminiApiKey = apiKeyInput.value.trim();
    localStorage.setItem("gemini_api_key", geminiApiKey);
    showToast("Gemini API Key saved successfully!", "success");
    apiPanel.classList.add("hidden");
});

// Dropzone Events
btnBrowse.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
});
dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
});
dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
});
dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files[0]);
    }
});
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFileUpload(fileInput.files[0]);
    }
});

// File Upload and Processing
async function handleFileUpload(file) {
    if (!geminiApiKey) {
        showToast("Please enter and save your Gemini API Key first!", "danger");
        apiPanel.classList.remove("hidden");
        return;
    }
    
    // UI Loading state
    uploadStatus.classList.remove("hidden");
    statusHeading.textContent = `Processing "${file.name}"...`;
    statusDetail.textContent = "Uploading document to Gemini API for OCR, structure extraction, and translations. This may take 10-25 seconds...";
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("api_key", geminiApiKey);
    
    try {
        const response = await fetch("/api/process", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Server error processing file");
        }
        
        const data = await response.json();
        if (!data.categories || data.categories.length === 0) {
            throw new Error("No items or categories could be extracted. Please make sure the image/file is readable.");
        }
        
        menuData = data;
        activeCategoryIndex = 0;
        
        showToast(`Menu successfully parsed! Extracted ${countItems()} items.`, "success");
        
        // Transition views
        uploadView.classList.remove("active");
        uploadView.classList.add("hidden");
        editorView.classList.remove("hidden");
        
        renderSidebar();
        renderActiveCategory();
        
    } catch (error) {
        console.error("Upload error:", error);
        showToast(error.message, "danger");
    } finally {
        uploadStatus.classList.add("hidden");
    }
}

function countItems() {
    return menuData.categories.reduce((acc, cat) => acc + (cat.items ? cat.items.length : 0), 0);
}

// Sidebar Rendering
function renderSidebar() {
    categoryList.innerHTML = "";
    menuData.categories.forEach((cat, index) => {
        const li = document.createElement("li");
        li.className = `category-item ${index === activeCategoryIndex ? 'active' : ''}`;
        li.addEventListener("click", () => {
            activeCategoryIndex = index;
            renderSidebar();
            renderActiveCategory();
        });
        
        const meta = document.createElement("div");
        meta.className = "category-meta";
        
        const enSpan = document.createElement("span");
        enSpan.className = "cat-en";
        enSpan.textContent = cat.name_en || `Category ${index + 1}`;
        
        const arSpan = document.createElement("span");
        arSpan.className = "cat-ar";
        arSpan.textContent = cat.name_ar || "";
        
        meta.appendChild(enSpan);
        meta.appendChild(arSpan);
        
        const badge = document.createElement("span");
        badge.className = "category-badge";
        badge.textContent = cat.items ? cat.items.length : 0;
        
        li.appendChild(meta);
        li.appendChild(badge);
        categoryList.appendChild(li);
    });
}

// Active Category Items Rendering
function renderActiveCategory() {
    const cat = menuData.categories[activeCategoryIndex];
    if (!cat) {
        activeCatTitleEn.textContent = "No Category Selected";
        activeCatTitleAr.textContent = "";
        itemsTableBody.innerHTML = "";
        return;
    }
    
    activeCatTitleEn.textContent = cat.name_en || "Unnamed Category";
    activeCatTitleAr.textContent = cat.name_ar || "";
    
    itemsTableBody.innerHTML = "";
    if (!cat.items || cat.items.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="7" style="text-align: center; color: var(--text-disabled); padding: 40px;">No items in this category. Click 'Add Item' to create one.</td>`;
        itemsTableBody.appendChild(tr);
        return;
    }
    
    cat.items.forEach((item, itemIdx) => {
        const tr = document.createElement("tr");
        
        // 1. Index
        const tdIdx = document.createElement("td");
        tdIdx.textContent = itemIdx + 1;
        tr.appendChild(tdIdx);
        
        // 2. Name EN Input
        const tdNameEn = document.createElement("td");
        const inputEn = document.createElement("input");
        inputEn.type = "text";
        inputEn.className = "cell-input";
        inputEn.value = item.name_en || "";
        inputEn.addEventListener("input", (e) => {
            item.name_en = e.target.value;
        });
        tdNameEn.appendChild(inputEn);
        tr.appendChild(tdNameEn);
        
        // 3. Name AR Input (Arabic direction)
        const tdNameAr = document.createElement("td");
        const inputAr = document.createElement("input");
        inputAr.type = "text";
        inputAr.className = "cell-input arabic-input";
        inputAr.value = item.name_ar || "";
        inputAr.addEventListener("input", (e) => {
            item.name_ar = e.target.value;
        });
        tdNameAr.appendChild(inputAr);
        tr.appendChild(tdNameAr);
        
        // 4. Item Type Dropdown
        const tdType = document.createElement("td");
        const selectType = document.createElement("select");
        selectType.className = "cell-select";
        const types = [
            { val: "non_veg", label: "Non-Vegetarian" },
            { val: "veg", label: "Vegetarian" },
            { val: "beverage", label: "Beverage" },
            { val: "dessert", label: "Dessert" }
        ];
        types.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t.val;
            opt.textContent = t.label;
            if (item.item_type === t.val) opt.selected = true;
            selectType.appendChild(opt);
        });
        selectType.addEventListener("change", (e) => {
            item.item_type = e.target.value;
            // Also sync tags with type
            item.tags = [e.target.value];
        });
        tdType.appendChild(selectType);
        tr.appendChild(tdType);
        
        // 5. Pricing Mode Selection
        const tdMode = document.createElement("td");
        const selectMode = document.createElement("select");
        selectMode.className = "cell-select";
        
        const hasOptions = item.options && item.options.length > 0;
        
        const optSingle = document.createElement("option");
        optSingle.value = "single";
        optSingle.textContent = "Single Price";
        
        const optMulti = document.createElement("option");
        optMulti.value = "multi";
        optMulti.textContent = "Multiple Sizes/Options";
        
        selectMode.appendChild(optSingle);
        selectMode.appendChild(optMulti);
        
        // Explicitly set value to match item's state *before* rendering contents
        selectMode.value = hasOptions ? "multi" : "single";
        
        tdMode.appendChild(selectMode);
        tr.appendChild(tdMode);
        
        // 6. Pricing Details
        const tdPrice = document.createElement("td");
        tdPrice.className = "price-container";
        
        let isInitializing = true;
        
        function renderPriceCellContents() {
            tdPrice.innerHTML = "";
            const mode = selectMode.value;
            
            if (mode === "single") {
                // Ensure options are cleared ONLY if this is a manual change after load
                if (!isInitializing) {
                    item.options = [];
                }
                const inputPrice = document.createElement("input");
                inputPrice.type = "number";
                inputPrice.step = "any";
                inputPrice.className = "cell-input";
                inputPrice.placeholder = "Price (e.g. 15.0)";
                inputPrice.value = item.price || "";
                inputPrice.addEventListener("input", (e) => {
                    item.price = parseFloat(e.target.value) || 0;
                });
                tdPrice.appendChild(inputPrice);
            } else {
                // Multi-price mode
                item.price = 0; // Base price is 0
                if (!item.options || item.options.length === 0) {
                    item.options = [
                        { name_en: "Half", name_ar: "نصف", price: 0.0 },
                        { name_en: "Full", name_ar: "كامل", price: 0.0 }
                    ];
                }
                
                const list = document.createElement("div");
                list.className = "modifiers-list";
                
                item.options.forEach((opt, optIdx) => {
                    const row = document.createElement("div");
                    row.className = "modifier-row";
                    
                    const nameEnInput = document.createElement("input");
                    nameEnInput.type = "text";
                    nameEnInput.className = "cell-input modifier-name-en";
                    nameEnInput.placeholder = "Size (EN)";
                    nameEnInput.value = opt.name_en || "";
                    nameEnInput.addEventListener("input", (e) => {
                        opt.name_en = e.target.value;
                    });
                    
                    const nameArInput = document.createElement("input");
                    nameArInput.type = "text";
                    nameArInput.className = "cell-input modifier-name-ar arabic-input";
                    nameArInput.placeholder = "حجم (AR)";
                    nameArInput.value = opt.name_ar || "";
                    nameArInput.addEventListener("input", (e) => {
                        opt.name_ar = e.target.value;
                    });
                    
                    const priceInput = document.createElement("input");
                    priceInput.type = "number";
                    priceInput.step = "any";
                    priceInput.className = "cell-input modifier-val";
                    priceInput.placeholder = "Price";
                    priceInput.value = opt.price !== undefined ? opt.price : "";
                    priceInput.addEventListener("input", (e) => {
                        opt.price = parseFloat(e.target.value) || 0;
                    });
                    
                    const btnRemoveOpt = document.createElement("button");
                    btnRemoveOpt.className = "btn-remove-modifier";
                    btnRemoveOpt.innerHTML = '<i class="fa-solid fa-xmark"></i>';
                    btnRemoveOpt.addEventListener("click", () => {
                        item.options.splice(optIdx, 1);
                        renderPriceCellContents();
                    });
                    
                    row.appendChild(nameEnInput);
                    row.appendChild(nameArInput);
                    row.appendChild(priceInput);
                    row.appendChild(btnRemoveOpt);
                    list.appendChild(row);
                });
                
                const btnAddOpt = document.createElement("button");
                btnAddOpt.className = "btn-add-modifier-option";
                btnAddOpt.innerHTML = '<i class="fa-solid fa-plus"></i> Add Option';
                btnAddOpt.addEventListener("click", () => {
                    item.options.push({ name_en: "Size", name_ar: "حجم", price: 0.0 });
                    renderPriceCellContents();
                });
                
                list.appendChild(btnAddOpt);
                tdPrice.appendChild(list);
            }
        }
        
        selectMode.addEventListener("change", (e) => {
            renderPriceCellContents();
        });
        
        renderPriceCellContents();
        isInitializing = false;
        tr.appendChild(tdPrice);
        
        // 7. Delete Item Button
        const tdDel = document.createElement("td");
        const btnDel = document.createElement("button");
        btnDel.className = "btn-icon btn-danger-text";
        btnDel.innerHTML = '<i class="fa-solid fa-trash"></i>';
        btnDel.addEventListener("click", () => {
            cat.items.splice(itemIdx, 1);
            renderSidebar();
            renderActiveCategory();
            showToast("Item deleted", "info");
        });
        tdDel.appendChild(btnDel);
        tr.appendChild(tdDel);
        
        itemsTableBody.appendChild(tr);
    });
}

// Category Dialog Helpers
function openCategoryDialog(mode = "add") {
    dialogMode = mode;
    categoryDialog.classList.remove("hidden");
    if (mode === "add") {
        catDialogTitle.textContent = "Add Category";
        catInputEn.value = "";
        catInputAr.value = "";
    } else {
        catDialogTitle.textContent = "Rename Category";
        const cat = menuData.categories[activeCategoryIndex];
        catInputEn.value = cat.name_en || "";
        catInputAr.value = cat.name_ar || "";
    }
}

function closeCategoryDialog() {
    categoryDialog.classList.add("hidden");
}

btnAddCategory.addEventListener("click", () => openCategoryDialog("add"));
btnEditActiveCat.addEventListener("click", () => openCategoryDialog("edit"));
btnCancelCat.addEventListener("click", closeCategoryDialog);

btnSaveCat.addEventListener("click", () => {
    const enVal = catInputEn.value.trim();
    const arVal = catInputAr.value.trim();
    
    if (!enVal && !arVal) {
        showToast("Category name cannot be completely empty!", "danger");
        return;
    }
    
    if (dialogMode === "add") {
        menuData.categories.push({
            name_en: enVal,
            name_ar: arVal,
            average_prep_time_minutes: 20,
            is_active: 1,
            items: []
        });
        activeCategoryIndex = menuData.categories.length - 1;
        showToast("Category added", "success");
    } else {
        const cat = menuData.categories[activeCategoryIndex];
        if (cat) {
            cat.name_en = enVal;
            cat.name_ar = arVal;
            showToast("Category updated", "success");
        }
    }
    
    closeCategoryDialog();
    renderSidebar();
    renderActiveCategory();
});

// Delete Category Action
btnDeleteActiveCat.addEventListener("click", () => {
    if (menuData.categories.length === 0) return;
    
    const cat = menuData.categories[activeCategoryIndex];
    const catName = cat.name_en || "this category";
    
    if (confirm(`Are you sure you want to delete "${catName}" and all of its items?`)) {
        menuData.categories.splice(activeCategoryIndex, 1);
        // Reset active index
        activeCategoryIndex = Math.max(0, activeCategoryIndex - 1);
        
        showToast("Category deleted", "info");
        renderSidebar();
        renderActiveCategory();
    }
});

// Add Item Action
btnAddItem.addEventListener("click", () => {
    const cat = menuData.categories[activeCategoryIndex];
    if (!cat) {
        showToast("Please create/select a category first!", "warning");
        return;
    }
    
    if (!cat.items) cat.items = [];
    
    cat.items.push({
        name_en: "New Item",
        name_ar: "عنصر جديد",
        description_en: "",
        description_ar: "",
        price: 0.0,
        options: [],
        tags: ["non_veg"],
        item_type: "non_veg"
    });
    
    renderSidebar(); // Update counts
    renderActiveCategory();
    
    // Scroll table to the bottom
    const tableWrapper = document.querySelector(".items-table-wrapper");
    tableWrapper.scrollTop = tableWrapper.scrollHeight;
    
    showToast("New item added to category", "success");
});

// Export to Excel
btnExportExcel.addEventListener("click", async () => {
    if (menuData.categories.length === 0) {
        showToast("There is no menu data to export!", "warning");
        return;
    }
    
    showToast("Generating spreadsheet...", "info");
    
    try {
        const response = await fetch("/api/export", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(menuData)
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Server error exporting Excel sheet");
        }
        
        const blob = await response.blob();
        
        // Trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "menu_digitized.xlsx";
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        a.remove();
        
        showToast("Excel spreadsheet downloaded successfully!", "success");
        
    } catch (error) {
        console.error("Export error:", error);
        showToast(error.message, "danger");
    }
});

// Shutdown Server Action
btnShutdown.addEventListener("click", async () => {
    if (confirm("Are you sure you want to stop the local server and exit RestOCR?")) {
        showToast("Stopping local server... You can close this window now.", "info");
        try {
            await fetch("/api/shutdown", { method: "POST" });
        } catch (e) {
            // Server might disconnect immediately
        }
        
        // Renders shutdown message
        document.body.innerHTML = `
            <div class="glow-container">
                <div class="glow-orb" style="background: rgba(239, 68, 68, 0.15)"></div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: 'Outfit', sans-serif;">
                <i class="fa-solid fa-power-off" style="font-size: 4rem; color: var(--danger); margin-bottom: 20px;"></i>
                <h1 style="font-size: 2rem; margin-bottom: 10px;">RestOCR Has Shut Down</h1>
                <p style="color: var(--text-secondary);">The local server was closed successfully. You can now close this browser tab.</p>
            </div>
        `;
    }
});

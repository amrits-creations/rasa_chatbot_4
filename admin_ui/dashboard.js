class AdminDashboard {
    constructor() {
        this.apiEndpoint = 'http://localhost:5000/api';
        this.token = localStorage.getItem('adminToken');
        this.user = JSON.parse(localStorage.getItem('adminUser') || '{}');
        this.currentSection = null;
        this.currentUpdateId = null;
        this.currentUpdateType = null;

        // Check authentication
        if (!this.token) {
            window.location.href = 'login.html';
            return;
        }

        this.initializeElements();
        this.initializeEventListeners();
        this.setupNavigation();
        this.updateUserInfo();
    }

    initializeElements() {
        // Forms
        this.createProductForm = document.getElementById('createProductForm');
        this.createOrderForm = document.getElementById('createOrderForm');
        this.createUserForm = document.getElementById('createUserForm');
        this.createFaqForm = document.getElementById('createFaqForm');
        this.createRoleForm = document.getElementById('createRoleForm');
        this.updateForm = document.getElementById('updateForm');

        // Table bodies
        this.productsTableBody = document.getElementById('productsTableBody');
        this.ordersTableBody = document.getElementById('ordersTableBody');
        this.usersTableBody = document.getElementById('usersTableBody');
        this.faqTableBody = document.getElementById('faqTableBody');
        this.unansweredTableBody = document.getElementById('unansweredTableBody');
        this.rolesTableBody = document.getElementById('rolesTableBody');

        // Other elements
        this.navTabs = document.getElementById('navTabs');
        this.updateModal = document.getElementById('updateModal');
        this.responseArea = document.getElementById('responseArea');
        this.responseText = document.getElementById('responseText');
        this.userInfo = document.getElementById('userInfo');
        this.logoutBtn = document.getElementById('logoutBtn');
    }

    initializeEventListeners() {
        // Form submissions
        this.createProductForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createProduct();
        });

        this.createOrderForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createOrder();
        });

        this.createUserForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createUser();
        });

        this.createFaqForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createFaq();
        });

        this.createRoleForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createRole();
        });

        this.updateForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitUpdate();
        });

        // Modal controls
        document.getElementById('cancelUpdate')?.addEventListener('click', () => {
            this.hideUpdateModal();
        });

        // Logout
        this.logoutBtn?.addEventListener('click', () => {
            this.logout();
        });

        // Close modal on outside click
        this.updateModal?.addEventListener('click', (e) => {
            if (e.target === this.updateModal) {
                this.hideUpdateModal();
            }
        });
    }

    setupNavigation() {
        const userRole = this.user.role;
        const availableSections = this.getAvailableSections(userRole);

        // Create navigation tabs
        this.navTabs.innerHTML = '';
        availableSections.forEach((section, index) => {
            const tab = document.createElement('button');
            tab.className = `nav-tab ${index === 0 ? 'active' : ''}`;
            tab.dataset.section = section.id;
            tab.textContent = section.label;
            tab.addEventListener('click', () => this.switchSection(section.id));
            this.navTabs.appendChild(tab);
        });

        // Show first available section
        if (availableSections.length > 0) {
            this.switchSection(availableSections[0].id);
        }
    }

    getAvailableSections(userRole) {
        const allSections = [
            { id: 'products', label: '📦 Products' },
            { id: 'orders', label: '📋 Orders' },
            { id: 'users', label: '👥 Users' },
            { id: 'faq', label: '❓ FAQ' },
            { id: 'unanswered', label: '❔ Unanswered' },
            { id: 'roles', label: '🔐 Roles' }
        ];

        const accessMap = {
            'Order Admin': ['orders'],
            'Product Admin': ['products', 'orders'],
            'Application Admin': ['users', 'products', 'orders', 'faq', 'unanswered'],
            'System Admin': ['roles', 'users', 'products', 'orders', 'faq', 'unanswered']
        };

        const allowedSections = accessMap[userRole] || [];
        return allSections.filter(section => allowedSections.includes(section.id));
    }

    switchSection(sectionId) {
        // Update tab active state
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.section === sectionId) {
                tab.classList.add('active');
            }
        });

        // Update content active state
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = sectionId;
            this.loadSectionData(sectionId);
        }
    }

    loadSectionData(sectionId) {
        switch (sectionId) {
            case 'products':
                this.loadProducts();
                break;
            case 'orders':
                this.loadOrders();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'faq':
                this.loadFaq();
                break;
            case 'unanswered':
                this.loadUnanswered();
                break;
            case 'roles':
                this.loadRoles();
                break;
        }
    }

    updateUserInfo() {
        this.userInfo.textContent = `Welcome, ${this.user.username} (${this.user.role})`;
    }

    async makeAuthenticatedRequest(url, options = {}) {
        const headers = {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                signal: AbortSignal.timeout(10000)
            });

            if (response.status === 401) {
                this.logout();
                return null;
            }

            return await response.json();
        } catch (error) {
            this.showResponse('Connection error. Please try again.', 'error');
            return null;
        }
    }

    // Products functionality
    async loadProducts() {
        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/products`);
        if (result && result.success) {
            this.displayProducts(result.data);
        }
    }

    displayProducts(products) {
        this.productsTableBody.innerHTML = '';
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.product_id}</td>
                <td>${product.product_name}</td>
                <td>${product.current_stock} ${product.quantity_type}</td>
                <td>${product.moq}</td>
                <td>${product.quantity_type}</td>
                <td>
                    <button class="btn btn-success btn-small" onclick="dashboard.showUpdateModal('products', ${product.product_id}, ${JSON.stringify(product).replace(/"/g, '&quot;')})">
                        📝 Edit
                    </button>
                    <button class="btn btn-danger btn-small" onclick="dashboard.deleteItem('products', ${product.product_id}, '${product.product_name}')">
                        🗑️ Delete
                    </button>
                </td>
            `;
            this.productsTableBody.appendChild(row);
        });
    }

    async createProduct() {
        const name = document.getElementById('productName').value.trim();
        const stock = parseInt(document.getElementById('initialStock').value) || 0;
        const moq = parseInt(document.getElementById('minOrderQty').value) || 1;
        const quantityType = document.getElementById('quantityType').value;

        if (!name) {
            this.showResponse('Product name is required', 'error');
            return;
        }

        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/products`, {
            method: 'POST',
            body: JSON.stringify({ name, stock, moq, quantity_type: quantityType })
        });

        if (result) {
            this.showResponse(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                this.createProductForm.reset();
                this.loadProducts();
            }
        }
    }

    // Orders functionality
    async loadOrders() {
        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/orders`);
        if (result && result.success) {
            this.displayOrders(result.data);
        }
    }

    displayOrders(orders) {
        this.ordersTableBody.innerHTML = '';
        orders.forEach(order => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${order.order_id}</td>
                <td>${order.username}</td>
                <td>${order.product_name}</td>
                <td><span class="status-badge status-${order.status.toLowerCase()}">${order.status}</span></td>
                <td>${order.estimated_delivery || 'Not set'}</td>
                <td>
                    <button class="btn btn-success btn-small" onclick="dashboard.showUpdateModal('orders', ${order.order_id}, ${JSON.stringify(order).replace(/"/g, '&quot;')})">
                        📝 Edit
                    </button>
                    <button class="btn btn-danger btn-small" onclick="dashboard.deleteItem('orders', ${order.order_id}, 'Order ${order.order_id}')">
                        🗑️ Delete
                    </button>
                </td>
            `;
            this.ordersTableBody.appendChild(row);
        });
    }

    async createOrder() {
        const userId = parseInt(document.getElementById('orderUserId').value);
        const productId = parseInt(document.getElementById('orderProductId').value);
        const status = document.getElementById('orderStatus').value;
        const estimatedDelivery = document.getElementById('estimatedDelivery').value;

        if (!userId || !productId) {
            this.showResponse('User ID and Product ID are required', 'error');
            return;
        }

        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/orders`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId, product_id: productId, status, estimated_delivery: estimatedDelivery })
        });

        if (result) {
            this.showResponse(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                this.createOrderForm.reset();
                this.loadOrders();
            }
        }
    }

    // Users functionality
    async loadUsers() {
        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/users`);
        if (result && result.success) {
            this.displayUsers(result.data);
        }
    }

    displayUsers(users) {
        this.usersTableBody.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.user_id}</td>
                <td>${user.username}</td>
                <td>${user.role_name}</td>
                <td>
                    <button class="btn btn-success btn-small" onclick="dashboard.showUpdateModal('users', ${user.user_id}, ${JSON.stringify(user).replace(/"/g, '&quot;')})">
                        📝 Edit
                    </button>
                    <button class="btn btn-danger btn-small" onclick="dashboard.deleteItem('users', ${user.user_id}, '${user.username}')">
                        🗑️ Delete
                    </button>
                </td>
            `;
            this.usersTableBody.appendChild(row);
        });
    }

    async createUser() {
        const username = document.getElementById('newUsername').value.trim();
        const password = document.getElementById('newPassword').value;
        const roleName = document.getElementById('newUserRole').value;

        if (!username || !password || !roleName) {
            this.showResponse('All fields are required', 'error');
            return;
        }

        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/users`, {
            method: 'POST',
            body: JSON.stringify({ username, password, role_name: roleName })
        });

        if (result) {
            this.showResponse(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                this.createUserForm.reset();
                this.loadUsers();
            }
        }
    }

    // FAQ functionality
    async loadFaq() {
        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/faq`);
        if (result && result.success) {
            this.displayFaq(result.data);
        }
    }

    displayFaq(faqs) {
        this.faqTableBody.innerHTML = '';
        faqs.forEach(faq => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${faq.faq_id}</td>
                <td>${faq.question}</td>
                <td>${faq.answer.substring(0, 100)}${faq.answer.length > 100 ? '...' : ''}</td>
                <td>
                    <button class="btn btn-success btn-small" onclick="dashboard.showUpdateModal('faq', ${faq.faq_id}, ${JSON.stringify(faq).replace(/"/g, '&quot;')})">
                        📝 Edit
                    </button>
                    <button class="btn btn-danger btn-small" onclick="dashboard.deleteItem('faq', ${faq.faq_id}, 'FAQ ${faq.faq_id}')">
                        🗑️ Delete
                    </button>
                </td>
            `;
            this.faqTableBody.appendChild(row);
        });
    }

    async createFaq() {
        const question = document.getElementById('faqQuestion').value.trim();
        const answer = document.getElementById('faqAnswer').value.trim();

        if (!question || !answer) {
            this.showResponse('Both question and answer are required', 'error');
            return;
        }

        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/faq`, {
            method: 'POST',
            body: JSON.stringify({ question, answer })
        });

        if (result) {
            this.showResponse(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                this.createFaqForm.reset();
                this.loadFaq();
            }
        }
    }

    // Unanswered Questions functionality
    async loadUnanswered() {
        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/unanswered`);
        if (result && result.success) {
            this.displayUnanswered(result.data);
        }
    }

    displayUnanswered(questions) {
        this.unansweredTableBody.innerHTML = '';
        questions.forEach(question => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${question.uq_id}</td>
                <td>${question.question}</td>
                <td><span class="status-badge status-${question.status.toLowerCase()}">${question.status}</span></td>
                <td>
                    <button class="btn btn-success btn-small" onclick="dashboard.showUpdateModal('unanswered', ${question.uq_id}, ${JSON.stringify(question).replace(/"/g, '&quot;')})">
                        📝 Edit Status
                    </button>
                    <button class="btn btn-danger btn-small" onclick="dashboard.deleteItem('unanswered', ${question.uq_id}, 'Question ${question.uq_id}')">
                        🗑️ Delete
                    </button>
                </td>
            `;
            this.unansweredTableBody.appendChild(row);
        });
    }

    // Roles functionality
    async loadRoles() {
        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/roles`);
        if (result && result.success) {
            this.displayRoles(result.data);
        }
    }

    displayRoles(roles) {
        this.rolesTableBody.innerHTML = '';
        roles.forEach(role => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${role.role_id}</td>
                <td>${role.role_name}</td>
                <td>
                    <button class="btn btn-danger btn-small" onclick="dashboard.deleteItem('roles', ${role.role_id}, '${role.role_name}')">
                        🗑️ Delete
                    </button>
                </td>
            `;
            this.rolesTableBody.appendChild(row);
        });
    }

    async createRole() {
        const roleName = document.getElementById('roleName').value.trim();

        if (!roleName) {
            this.showResponse('Role name is required', 'error');
            return;
        }

        const result = await this.makeAuthenticatedRequest(`${this.apiEndpoint}/roles`, {
            method: 'POST',
            body: JSON.stringify({ role_name: roleName })
        });

        if (result) {
            this.showResponse(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                this.createRoleForm.reset();
                this.loadRoles();
            }
        }
    }

    // Modal functionality
    showUpdateModal(type, id, data) {
        this.currentUpdateType = type;
        this.currentUpdateId = id;

        const modalTitle = document.getElementById('modalTitle');
        const modalFields = document.getElementById('modalFields');

        modalTitle.textContent = `Update ${type.charAt(0).toUpperCase() + type.slice(1, -1)}`;
        modalFields.innerHTML = '';

        // Generate fields based on type
        const fields = this.getUpdateFields(type, data);
        fields.forEach(field => {
            const div = document.createElement('div');
            div.className = 'form-group';
            
            if (field.type === 'textarea') {
                div.innerHTML = `
                    <label for="${field.id}">${field.label}:</label>
                    <textarea id="${field.id}" ${field.required ? 'required' : ''} rows="4" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">${field.value || ''}</textarea>
                `;
            } else if (field.type === 'select') {
                const options = field.options.map(opt => `<option value="${opt.value}" ${opt.value === field.value ? 'selected' : ''}>${opt.label}</option>`).join('');
                div.innerHTML = `
                    <label for="${field.id}">${field.label}:</label>
                    <select id="${field.id}" ${field.required ? 'required' : ''}>${options}</select>
                `;
            } else {
                div.innerHTML = `
                    <label for="${field.id}">${field.label}:</label>
                    <input type="${field.type}" id="${field.id}" value="${field.value || ''}" ${field.required ? 'required' : ''}>
                `;
            }
            
            modalFields.appendChild(div);
        });

        this.updateModal.style.display = 'flex';
    }

    getUpdateFields(type, data) {
        const fields = {
            products: [
                { id: 'updateProductName', label: 'Product Name', type: 'text', value: data.product_name, required: true },
                { id: 'updateStock', label: 'Stock', type: 'number', value: data.current_stock },
                { id: 'updateMoq', label: 'MOQ', type: 'number', value: data.moq },
                { id: 'updateQuantityType', label: 'Quantity Type', type: 'select', value: data.quantity_type, 
                  options: [
                    { value: 'pcs', label: 'Pieces' },
                    { value: 'kg', label: 'Kilograms' },
                    { value: 'ltr', label: 'Liters' }
                  ]
                }
            ],
            orders: [
                { id: 'updateOrderStatus', label: 'Status', type: 'select', value: data.status,
                  options: [
                    { value: 'pending', label: 'Pending' },
                    { value: 'processing', label: 'Processing' },
                    { value: 'shipped', label: 'Shipped' },
                    { value: 'delivered', label: 'Delivered' }
                  ]
                },
                { id: 'updateEstimatedDelivery', label: 'Estimated Delivery', type: 'date', value: data.estimated_delivery }
            ],
            users: [
                { id: 'updateUsername', label: 'Username', type: 'text', value: data.username },
                { id: 'updatePassword', label: 'New Password', type: 'password', value: '' },
                { id: 'updateUserRole', label: 'Role', type: 'select', value: data.role_name,
                  options: [
                    { value: 'End User', label: 'End User' },
                    { value: 'Order Admin', label: 'Order Admin' },
                    { value: 'Product Admin', label: 'Product Admin' },
                    { value: 'Application Admin', label: 'Application Admin' },
                    { value: 'System Admin', label: 'System Admin' }
                  ]
                }
            ],
            faq: [
                { id: 'updateFaqQuestion', label: 'Question', type: 'text', value: data.question, required: true },
                { id: 'updateFaqAnswer', label: 'Answer', type: 'textarea', value: data.answer, required: true }
            ],
            unanswered: [
                { id: 'updateUnansweredStatus', label: 'Status', type: 'select', value: data.status,
                  options: [
                    { value: 'new', label: 'New' },
                    { value: 'reviewed', label: 'Reviewed' },
                    { value: 'resolved', label: 'Resolved' }
                  ]
                }
            ]
        };

        return fields[type] || [];
    }

    hideUpdateModal() {
        this.currentUpdateType = null;
        this.currentUpdateId = null;
        this.updateModal.style.display = 'none';
        this.updateForm.reset();
    }

    async submitUpdate() {
        if (!this.currentUpdateType || !this.currentUpdateId) return;

        const updateData = {};
        const fields = this.getUpdateFields(this.currentUpdateType, {});

        fields.forEach(field => {
            const element = document.getElementById(field.id);
            if (element && element.value) {
                const key = field.id.replace(/^update/, '').toLowerCase().replace(/([A-Z])/g, '_$1');
                updateData[key] = element.value;
            }
        });

        const result = await this.makeAuthenticatedRequest(
            `${this.apiEndpoint}/${this.currentUpdateType}/${this.currentUpdateId}`,
            {
                method: 'PUT',
                body: JSON.stringify(updateData)
            }
        );

        if (result) {
            this.showResponse(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                this.hideUpdateModal();
                this.loadSectionData(this.currentSection);
            }
        }
    }

    async deleteItem(type, id, name) {
        if (!confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
            return;
        }

        const result = await this.makeAuthenticatedRequest(
            `${this.apiEndpoint}/${type}/${id}`,
            { method: 'DELETE' }
        );

        if (result) {
            this.showResponse(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                this.loadSectionData(this.currentSection);
            }
        }
    }

    showResponse(message, type) {
        this.responseText.textContent = message;
        this.responseArea.className = `response-area ${type}`;
        this.responseArea.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.responseArea.style.display = 'none';
        }, 5000);
    }

    async logout() {
        await this.makeAuthenticatedRequest(`${this.apiEndpoint}/logout`, {
            method: 'POST'
        });

        localStorage.removeItem('adminToken');
        localStorage.removeItem('adminUser');
        window.location.href = 'login.html';
    }
}

// Global reference for button callbacks
let dashboard;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new AdminDashboard();
});


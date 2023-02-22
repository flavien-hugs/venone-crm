window.addEventListener('DOMContentLoaded', event => {
    var app = Vue.createApp({
        data() {
            return {
                tenants: [],
                perPage: 20,
                currentPage: 1,
                totalPages: 1,
                isLoading: false,
                tenantUUID: null,
                showDeleteAlert: false,
            }
        },
        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"]
        },

        mounted() {
            this.getTenants()
        },

        methods: {
            getTenants() {
                this.isLoading = true
                fetch(`/api/tenants/?page=` + this.currentPage, {
                    method: "GET",
                    headers: {
                        'Content-type': 'application/json'
                    }
                })
                .then((response) => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                })
                .then((data) => {
                    this.tenants = data.tenants;
                    this.totalPages = Math.ceil(data.total / this.perPage);
                    this.isLoading = false;
                })
                .catch((error) => {
                    console.error("FETCH ERROR:", error);
                    this.tenants = error;
                });
            },

            deleteTenantConfirm(tenantUUID) {
                this.tenantUUID = tenantUUID;
                const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
                modal.show();
            },

            onDeleteTenant() {
                const deleteURL = `/api/tenant/${this.tenantUUID}/delete/`;
                fetch(deleteURL, {
                    method: "DELETE",
                    headers: {
                        'Content-type': 'application/json'
                    }
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        this.tenants = this.tenants.filter(tenant => tenant.tenant_uuid !== this.tenantUUID);
                        this.getTenants();
                        this.tenantUUID = null;
                        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmModal'));
                        modal.hide();
                        this.showDeleteAlert = true;
                        console.log(data.message);
                        setTimeout(() => {
                            this.showDeleteAlert = false;
                        }, 3000);
                    } else {
                        console.log(data.message);
                    }
                })
                .catch((error) => console.error(error));
            },

            prevPage() {
                if (this.currentPage > this.totalPages) {
                    this.currentPage--;
                    this.getTenants();
                }
                window.scrollTo({top: 0, behavior: 'smooth'});
            },

            nextPage() {
                if (this.currentPage <= this.totalPages) {
                    this.currentPage++;
                    this.getTenants();
                }
                window.scrollTo({top: 0, behavior: 'smooth'});
            },
        },
    })

    app.mount('#tenantTable');
});
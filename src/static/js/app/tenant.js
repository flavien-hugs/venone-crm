import paginateComponent from './components/paginateComponent.js';
import messageComponent from './components/messageComponent.js';

window.addEventListener('DOMContentLoaded', event => {
    const OWNER_DATA = {
        owner_uuid: '',
        fullname: '',
        addr_email: '',
        percent: '',
        card_number: '',
        profession: '',
        location: '',
        parent_name: '',
        parent_name: '',
        phonenumber_one: '',
        phonenumber_two: ''
    };

    const HOUSE_DATA = {
        house_uuid: '',
        house_type: '',
        house_rent: '',
        house_guaranty: '',
        house_month: '',
        house_location: '',
        house_number_room: '',
        house_address: '',
        house_lease_start_date: new Date().toISOString().substring(0, 10),
    };

    const TENANT_DATA = {
        tenant_uuid: '',
        fullname: '',
        addr_email: '',
        card_number: '',
        profession: '',
        location: '',
        parent_name: '',
        parent_name: '',
        phonenumber_one: '',
        phonenumber_two: ''
    };

    var app = Vue.createApp({

        components: {
            paginateComponent,
            messageComponent,
        },

        data() {
            return {
                tenant: [],
                tenants: [],

                user: [],

                searchQuery: "",
                perPage: 10,
                currentStep: 1,
                currentPage: 1,
                totalPages: 1,
                isLoading: false,

                deleteTenantUUID: null,
                messageAlert: "",
                showMessageAlert: false,
                ownerData: { ...OWNER_DATA },
                houseData: { ...HOUSE_DATA },
                tenantData: { ...TENANT_DATA },
            }
        },
        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"]
        },

        watch: {
            'houseData.house_rent': function (f){
                this.houseData.house_rent = this.filterNumber(f);
            },
            'houseData.house_number_room': function (f){
                this.houseData.house_number_room = this.filterNumber(f);
            },
            'houseData.vn_house_month': function (f){
                this.houseData.vn_house_month = this.filterNumber(f);
            },
            'houseData.house_month': function (f){
                this.houseData.house_month = this.filterNumber(f);
            },
            'houseData.house_guaranty': function (f){
                this.houseData.house_guaranty = this.filterNumber(f);
            },

            searchQuery: function() {
                this.filteredTenants;
            }
        },

        mounted() {
            this.getTenants();
        },

        computed: {
            filteredTenants() {
                if (!this.searchQuery) {
                    return this.tenants;
                }

                const searchRegex = new RegExp(this.searchQuery, 'i');

                    return this.tenants.filter(tenant => {
                        const fullnameMatch = searchRegex.test(tenant.fullname);
                        const addrEmailMatch = searchRegex.test(tenant.addr_email);
                        const phonenumberOneMatch = searchRegex.test(tenant.phonenumber_one);
                        const phonenumberTwoMatch = searchRegex.test(tenant.phonenumber_two);
                        const cardNumberMatch = searchRegex.test(tenant.card_number);

                    return (
                        fullnameMatch ||
                        addrEmailMatch ||
                        phonenumberOneMatch ||
                        phonenumberTwoMatch ||
                        cardNumberMatch
                    );
                });
            },
        },

        methods: {
            nextStep() {
                this.currentStep++;
            },

            prevStep() {
                this.currentStep--;
            },

            filterNumber(e) {
                return  ("" + e).replace(/[^0-9]/g, '');
            },

            downloadTenantCSV() {
                window.location.href = `/dashboard/export-tenants-data`;
            },

            formatPhoneNumber(n) {
                return ("" + n)
                    .replace(/\D/g, "")
                    .substring(0, 15)
                    .replace(/(\d{2})(\d{4})(\d{4})/g, "$1-$2-$3");
            },

            async getTenants() {
                try {
                    this.isLoading = true;
                    const tenantURL = `/api/tenants/?page=${this.currentPage}&per_page=${this.perPage}&q=${this.searchQuery}`;

                    const response = await fetch(tenantURL, {
                        method: "GET",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    this.isLoading = false;

                    if (response.status == 200) {
                        const data = await response.json();
                        this.tenants = data.tenants;
                        this.user = data.user;
                        this.totalPages = Math.ceil(data.total / this.perPage);
                        this.currentPage = data.page;
                    } else {
                        this.isLoading = false;
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                } catch (error) {
                    console.error("FETCH ERROR:", error);
                }
            },

            createOwnerTenant() {
                const modal = new bootstrap.Modal(document.getElementById('addOwnerTenantModal'));
                modal.show();
            },

            createCompanyTenant() {
                const modal = new bootstrap.Modal(document.getElementById('createTenantModal'));
                modal.show();
            },

            updateTenant(tenant) {
                this.tenantData = { ...tenant } ?? {};
                const modal = new bootstrap.Modal(document.getElementById('updateTenantConfirm'));
                modal.show();
            },

            deleteTenantConfirm(tenantUUID) {
                this.deleteTenantUUID = tenantUUID;
                const modal = new bootstrap.Modal(document.getElementById('delTenantConfirmModal'));
                modal.show();
            },

            async onCreateOwnerTenant() {
                try {
                    const ownerTenantRegisterURL = `/api/owners/tenant-register/`;
                    const response = await fetch(ownerTenantRegisterURL, {
                        method: "POST",
                        headers: {
                            'Content-type': 'application/json'
                        },
                        body: JSON.stringify({
                            house_data: this.houseData,
                            tenant_data: this.tenantData
                        }),
                    });

                    const data = await response.json();

                    if (data.success) {
                        await this.getTenants();
                        this.tenantData = { ...TENANT_DATA };
                        this.houseData = { ...HOUSE_DATA };
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                    }
                } catch (error) {
                    console.log(error);
                    this.showMessageAlert = true;
                    this.messageAlert = "Une erreur est survenue lors de l'ajout de ce locataire";
                } finally {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addOwnerTenantModal'));
                    modal.hide();
                }
            },

            async onUpdateTenant() {
                try {
                    const updateURL = `/api/tenants/${this.tenantData.tenant_uuid}/update/`;
                    const response = await fetch(updateURL, {
                        method: "PUT",
                        headers: {'Content-type': 'application/json'},
                        body: JSON.stringify(this.tenantData),
                    });

                    const data = await response.json();

                    if (data.success) {
                        const index = this.tenants.findIndex(tenant => tenant.tenant_uuid === this.tenantData.tenant_uuid);
                        this.tenants.splice(index, 1, this.tenantData);
                        this.tenantData = { ...TENANT_DATA };
                        this.getTenants();

                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                    }
                } catch (error) {
                    console.log(error);
                    this.showMessageAlert = true;
                    this.messageAlert = "Une erreur est survenue lors de la mise à jour de ce locataire";
                } finally {
                    this.tenantData.tenant_uuid = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('updateTenantConfirm'));
                    modal.hide();
                }
            },

            async onCreateComapnyTenant() {
                try {
                    const registerURL = `/api/companies/tenant-register/`;

                    if (
                        this.ownerData.percent === "" ||
                        isNaN(this.ownerData.percent) ||
                        this.ownerData.percent < 0 ||
                        this.ownerData.percent > 100
                    ) {
                        this.showMessageAlert = true;
                        this.messageAlert =
                            "Valeur de pourcentage invalide. Le pourcentage doit être un nombre entre 0 et 100.";
                        return;
                    }

                    this.ownerData.percent = parseFloat(this.ownerData.percent);

                    const response = await fetch(registerURL, {
                        method: "POST",
                        headers: {
                            'Content-type': 'application/json'
                        },
                        body: JSON.stringify({
                            owner_data: this.ownerData,
                            house_data: this.houseData,
                            tenant_data: this.tenantData
                        }),
                    });

                    const data = await response.json();
                    if (data.success) {
                        await this.getTenants();
                        this.ownerData = { ...OWNER_DATA };
                        this.houseData = { ...HOUSE_DATA };
                        this.tenantData = { ...TENANT_DATA };
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                    }
                } catch (error) {
                    console.log(error);
                    this.showMessageAlert = true;
                    this.messageAlert = "Une erreur est survenue lors de l'ajout du locataire";
                } finally {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('createTenantModal'));
                    modal.hide();
                }
            },

            async onDeleteTenant() {
                try {
                    const deleteURL = `/api/tenants/${this.deleteTenantUUID}/delete/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.tenants = this.tenants.filter(tenant => tenant.tenant_uuid !== this.deleteTenantUUID);
                        await this.getTenants();
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                    }
                } catch (error) {
                    console.log(error);
                    this.showMessageAlert = true;
                    this.messageAlert = "Une erreur est survenue lors de la suppression de ce locataire";
                } finally {
                    this.deleteTenantUUID = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('delTenantConfirmModal'));
                    modal.hide();
                }
            },

            prevPage() {
                this.currentPage--;
                this.getTenants();
                window.scrollTo({top: 0, behavior: 'smooth'});
            },

            nextPage() {
                this.currentPage++;
                this.getTenants();
                window.scrollTo({top: 0, behavior: 'smooth'});
            },
        }
    })

    app.mount('#tenantTable');
});

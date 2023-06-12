import paginateComponent from './components/paginateComponent.js';
import messageComponent from './components/messageComponent.js';

window.addEventListener('DOMContentLoaded', event => {

    const OWNER_DATA = {
        uuid: '',
        vn_owner_id: '',
        vn_fullname: '',
        vn_addr_email: '',
        vn_cni_number: '',
        vn_location: '',
        vn_profession: '',
        vn_parent_name: '',
        vn_phonenumber_one: '',
        vn_phonenumber_two: '',
        vn_owner_percent: '',
    };

    const HOUSE_DATA = {
        uuid: '',
        vn_house_type: '',
        vn_house_rent: '',
        vn_house_guaranty: '',
        vn_house_month: '',
        vn_house_number_room: '',
        vn_house_address: '',
        vn_house_lease_start_date: new Date().toISOString().substring(0, 10),
    };

    const TENANT_DATA = {
        uuid: '',
        vn_tenant_id: '',
        vn_fullname: '',
        vn_addr_email: '',
        vn_cni_number: '',
        vn_location: '',
        vn_profession: '',
        vn_parent_name: '',
        vn_phonenumber_one: '',
        vn_phonenumber_two: '',
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
            'houseData.vn_house_month': function () {
                this.houseData.vn_house_guaranty = this.calculateGuaranty();
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
                        const fullnameMatch = searchRegex.test(tenant.vn_fullname);
                        const addrEmailMatch = searchRegex.test(tenant.vn_addr_email);
                        const phonenumberOneMatch = searchRegex.test(tenant.vn_phonenumber_one);
                        const phonenumberTwoMatch = searchRegex.test(tenant.vn_phonenumber_two);
                        const cardNumberMatch = searchRegex.test(tenant.vn_cni_number);

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

            downloadTenantCSV() {
                window.location.href = `/dashboard/export-tenants-data`;
            },

            calculateGuaranty() {
                const hrent = parseFloat(this.houseData.vn_house_rent);
                const hmonth = parseInt(this.houseData.vn_house_month);

                if (!isNaN(hrent) && !isNaN(hmonth)) {
                    return hrent * hmonth;
                } else {
                    return null;
                }
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
                        this.totalPages = Math.ceil(data.total / data.per_page);
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
                    const updateURL = `/api/tenants/${this.tenantData.uuid}/`;
                    const response = await fetch(updateURL, {
                        method: "PATCH",
                        headers: {'Content-type': 'application/json'},
                        body: JSON.stringify({update_tenant_data: this.tenantData}),
                    });

                    const data = await response.json();

                    if (data.success) {
                        const index = this.tenants.findIndex(tenant => tenant.uuid === this.tenantData.uuid);
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
                    this.tenantData.uuid = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('updateTenantConfirm'));
                    modal.hide();
                }
            },

            async onCreateComapnyTenant() {
                try {
                    const registerURL = `/api/companies/tenant-register/`;

                    if (
                        this.ownerData.vn_owner_percent === "" ||
                        Number.isNaN(parseFloat(this.ownerData.vn_owner_percent)) ||
                        this.ownerData.vn_owner_percent < 0 ||
                        this.ownerData.vn_owner_percent > 100
                    ) {
                        this.showMessageAlert = true;
                        this.messageAlert = "La valeur du pourcentage est invalide. Le pourcentage doit être un nombre entre 0 et 100.";
                        return;
                    }

                    this.ownerData.vn_owner_percent = parseFloat(this.ownerData.vn_owner_percent);

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

                    const { success, message } = await response.json();

                    if (success) {
                        await this.getTenants();
                        this.ownerData = { ...OWNER_DATA };
                        this.houseData = { ...HOUSE_DATA };
                        this.tenantData = { ...TENANT_DATA };
                        this.showMessageAlert = true;
                        this.messageAlert = message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = message;
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
                    const deleteURL = `/api/tenants/${this.deleteTenantUUID}/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    const { success, message } = await response.json();

                    if (success) {
                        this.tenants = this.tenants.filter(tenant => tenant.uuid !== this.deleteTenantUUID);
                        await this.getTenants();
                        this.showMessageAlert = true;
                        this.messageAlert = message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = message;
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

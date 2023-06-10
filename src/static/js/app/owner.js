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
                user: [],

                owners: [],
                owner: [],
                perPage: 20,
                currentStep: 1,
                currentPage: 1,
                totalPages: 1,
                ownerUUID: null,

                messageAlert: "",
                showMessageAlert: false,

                isLoading: false,
                ownerData: { ...OWNER_DATA },
                houseData: { ...HOUSE_DATA },
                tenantData: { ...TENANT_DATA },
            };
        },

        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"],
        },

        watch: {
            'houseData.vn_house_month': function () {
                this.houseData.vn_house_guaranty = this.calculateGuaranty();
            },
        },

        mounted() {
            this.getOwners();
        },

        methods: {

            calculateGuaranty() {
                const hrent = parseFloat(this.houseData.vn_house_rent);
                const hmonth = parseInt(this.houseData.vn_house_month);

                if (!isNaN(hrent) && !isNaN(hmonth)) {
                    return hrent * hmonth;
                } else {
                    return null;
                }
            },

            nextStep() {
                this.currentStep++;
            },

            prevStep() {
                this.currentStep--;
            },

            downloadOwnerCSV() {
                window.location.href = `/dashboard/export-owners-data`;
            },

            async getOwners() {
                try {
                    this.isLoading = true;
                    const ownersURL = `/api/owners/?page==${this.currentPage}`;

                    const response = await fetch(ownersURL, {
                        method: "GET",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.user = data.user;
                        this.owners = data.houseowners;
                        this.totalPages = Math.ceil(data.total / this.perPage);
                        this.isLoading = false;
                    } else {
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                } catch (error) {
                    console.error("FETCH ERROR:", error);
                    this.owners = error;
                }
            },

            async getOwner(uuid) {
                try {
                    const ownerURL = `/api/owners/${uuid}/`;
                    const response = await fetch(ownerURL, {
                        method: "GET",
                        headers: { "Content-type": "application/json" },
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.owner = data.owner;
                        const modal = new bootstrap.Modal(
                            document.getElementById("detailModal")
                        );
                        modal.show();
                    } else {
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                } catch (error) {
                    console.error("FETCH ERROR:", error);
                }
            },

            updateOwnerConfirm(owner) {
                this.ownerData = { ...owner } ?? {};
                const modal = new bootstrap.Modal(
                    document.getElementById("editModal")
                );
                modal.show();
            },

            deleteOwnerConfirm(uuid) {
                this.uuid = uuid;
                const modal = new bootstrap.Modal(
                    document.getElementById("deleteModal")
                );
                modal.show();
            },

            createOwnerTenantConfirm(uuid) {
                this.uuid = uuid;
                this.houseData = { ...uuid } ?? {};
                this.tenantData = { ...uuid } ?? {};
                const modal = new bootstrap.Modal(
                    document.getElementById("addOwnerTenantModal")
                );
                modal.show();
            },

            async onCreateOwnerTenant() {
                try {
                    const registerURL = `/api/owners/${this.uuid}/create-tenant/`;
                    const response = await fetch(registerURL, {
                        method: "POST",
                        headers: {
                            "Content-type": "application/json",
                        },
                        body: JSON.stringify({
                            house_data: this.houseData,
                            tenant_data: this.tenantData,
                        }),
                    });

                    const { success, message } = await response.json();

                    if (success) {
                        await this.getOwners();
                        this.tenantData = { ...TENANT_DATA };
                        this.houseData = { ...HOUSE_DATA };
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
                    console.error(error);
                    this.showMessageAlert = true;
                    this.messageAlert =
                        "Une erreur est survenue lors de la création du locataire.";
                } finally {
                    const modelElement = document.getElementById(
                        "addOwnerTenantModal"
                    );
                    const modal = bootstrap.Modal.getInstance(modelElement);
                    modal.hide();
                }
            },

            async onUpdateOwner() {
                try {
                    const updateURL = `/api/owners/${this.ownerData.uuid}/`;

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

                    const response = await fetch(updateURL, {
                        method: "PATCH",
                        headers: { "Content-type": "application/json" },
                        body: JSON.stringify(this.ownerData),
                    });

                    const { success, message } = await response.json();

                    if (success) {
                        const ownerUUID = this.ownerData.uuid;
                        const ownerIndex = this.owners.findIndex((owner) => owner.uuid === ownerUUID);
                        this.owners.splice(ownerIndex, 1, this.ownerData);
                        this.ownerData = { ...OWNER_DATA };
                        await this.getOwners();

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
                    this.showMessageAlert = true;
                    this.messageAlert = "Une erreur est survenue lors de la mise à jour du compte propriétaire.";
                } finally {
                    this.ownerData.uuid = null;
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("editModal")
                    );
                    modal.hide();
                }
            },

            async onDeleteOwner() {
                try {
                    const deleteURL = `/api/owners/${this.uuid}/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.owners = this.owners.filter(
                            (owner) => owner.owner_uuid !== this.uuid
                        );
                        await this.getOwners();
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
                    console.error(error);
                    this.showMessageAlert = true;
                    this.messageAlert =
                        "Une erreur est survenue lors de la suppresion de ce propriétaire.";
                } finally {
                    this.uuid = null;
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("deleteModal")
                    );
                    modal.hide();
                }
            },

            prevPage() {
                this.currentPage--;
                this.getOwners();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },

            nextPage() {
                this.currentPage++;
                this.getOwners();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },
        },
    });

    app.mount('#houseOwnerTable');
});

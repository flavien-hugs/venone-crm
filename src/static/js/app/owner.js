import paginateComponent from './components/paginateComponent.js';
import messageComponent from './components/messageComponent.js';

window.addEventListener('DOMContentLoaded', event => {

    const OWNER_DATA = {
        owner_uuid: '',
        gender: '',
        fullname: '',
        addr_email: '',
        card_number: '',
        location: '',
        percent: '',
        profession: '',
        parent_name: '',
        phonenumber_one: '',
        phonenumber_two: '',
    };

    const HOUSE_DATA = {
        house_uuid: '',
        house_type: '',
        house_rent: '',
        house_guaranty: '',
        house_month: '',
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
        parent_name: '',
        location: '',
        phonenumber_one: '',
        phonenumber_two: '',
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
            "ownerData.percent": function (f) {
                this.ownerData.percent = this.filterNumber(f);
            },
        },

        mounted() {
            this.getOwners();
        },

        methods: {
            filterNumber(e) {
                return ("" + e).replace(/[^0-9]/g, "");
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

                    if (response.status == 200) {
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

            async getOwner(ownerUUID) {
                try {
                    const ownerURL = `/api/owners/${ownerUUID}/`;
                    const response = await fetch(ownerURL, {
                        method: "GET",
                        headers: { "Content-type": "application/json" },
                    });

                    if (response.status == 200) {
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

            deleteOwnerConfirm(ownerUUID) {
                this.ownerUUID = ownerUUID;
                const modal = new bootstrap.Modal(
                    document.getElementById("deleteModal")
                );
                modal.show();
            },

            createOwnerTenantConfirm(ownerUUID) {
                this.ownerUUID = ownerUUID;
                this.houseData = { ...ownerUUID } ?? {};
                this.tenantData = { ...ownerUUID } ?? {};
                const modal = new bootstrap.Modal(
                    document.getElementById("addOwnerTenantModal")
                );
                modal.show();
            },

            async onCreateOwnerTenant() {
                try {
                    const registerURL = `/api/owners/${this.ownerUUID}/create_tenant/`;
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

                    const data = await response.json();

                    if (data.success) {
                        await this.getOwners();
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
                    const updateURL = `/api/owners/${this.ownerData.owner_uuid}/update/`;

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

                    const response = await fetch(updateURL, {
                        method: "PUT",
                        headers: { "Content-type": "application/json" },
                        body: JSON.stringify(this.ownerData),
                    });

                    const data = await response.json();

                    if (data.success) {
                        const index = this.owners.findIndex(
                            (owner) =>
                                owner.owner_uuid === this.ownerData.owner_uuid
                        );
                        this.owners.splice(index, 1, this.ownerData);
                        this.ownerData = { ...OWNER_DATA };
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
                    this.showMessageAlert = true;
                    this.messageAlert =
                        "Une erreur est survenue lors de la mise à du compte propriétaire.";
                } finally {
                    this.ownerData.owner_uuid = null;
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("editModal")
                    );
                    modal.hide();
                }
            },

            async onDeleteOwner() {
                try {
                    const deleteURL = `/api/owners/${this.ownerUUID}/delete/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.owners = this.owners.filter(
                            (owner) => owner.owner_uuid !== this.ownerUUID
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
                    this.ownerUUID = null;
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

window.addEventListener('DOMContentLoaded', event => {
    const OWNER_DATA = {
        owner_uuid: '',
        gender: '',
        fullname: '',
        addr_email: '',
        card_number: '',
        location: '',
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
        data() {
            return {
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
                tenantData: { ...TENANT_DATA }
            }
        },

        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"]
        },

        mounted() {
            this.getOwners()
        },

        methods: {

            nextStep() {
                this.currentStep++;
            },

            prevStep() {
                this.currentStep--;
            },

            async getOwners() {
                try {
                    this.isLoading = true;
                    const ownersURL = `/api/owners/?page==${this.currentPage}`;

                    const response = await fetch(ownersURL, {
                        method: "GET",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    if (response.ok) {
                        const data = await response.json();
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
                    const ownerURL = `/api/owner/${ownerUUID}/`;
                    const response = await fetch(ownerURL, {
                        method: "GET",
                        headers: {'Content-type': 'application/json'},
                    });

                    const data = await response.json();
                    this.owner = data.owner;

                    const modal = new bootstrap.Modal(document.getElementById('detailModal'));
                    modal.show();
                } catch (error) {
                    console.error(error);
                }
            },

            updateOwnerConfirm(owner) {
                this.ownerData = { ...owner } ?? {};
                const modal = new bootstrap.Modal(document.getElementById('editModal'));
                modal.show();
            },

            deleteOwnerConfirm(ownerUUID) {
                this.ownerUUID = ownerUUID;
                const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
                modal.show();
            },

            createOwnerTenantConfirm(ownerUUID) {
                this.ownerUUID = ownerUUID;
                this.houseData = { ...ownerUUID } ?? {};
                this.tenantData = { ...ownerUUID } ?? {};
                const modal = new bootstrap.Modal(document.getElementById('addOwnerTenantModal'));
                modal.show();
            },

            async onCreateOwnerTenant() {
                try {
                    const registerURL = `/api/owner/${this.ownerUUID}/create_tenant/`;
                    const response = await fetch(registerURL, {
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
                        await this.getOwners();
                        this.houseData = { ...HOUSE_DATA };
                        this.tenantData = { ...TENANT_DATA };
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.messageAlert = data.message;
                    }
                } catch (error) {
                    console.error(error);
                } finally {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addOwnerTenantModal'));
                    modal.hide();
                }
            },

            async onUpdateOwner() {
                try {
                    const updateURL = `/api/owner/${this.ownerData.owner_uuid}/update/`;
                    const response = await fetch(updateURL, {
                        method: "PUT",
                        headers: {'Content-type': 'application/json'},
                        body: JSON.stringify(this.ownerData),
                    });

                    const data = await response.json();

                    if (data.success) {
                        const index = this.owners.findIndex(owner => owner.owner_uuid === this.ownerData.owner_uuid);
                        this.owners.splice(index, 1, this.ownerData);
                        this.ownerData = { ...OWNER_DATA };
                        await this.getOwners();

                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        console.log(data.message);
                    }
                } catch (error) {
                    console.error(error);
                } finally {
                    this.ownerData.owner_uuid = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                    modal.hide();
                }
            },

            async onDeleteOwner() {
                try {
                    const deleteURL = `/api/owner/${this.ownerUUID}/delete/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.owners = this.owners.filter(owner => owner.owner_uuid !== this.ownerUUID);
                        await this.getOwners();
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        console.log(data.message);
                    }
                } catch (error) {
                    console.error(error);
                } finally {
                    this.ownerUUID = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('confirmModal'));
                    modal.hide();
                }
            },

            prevPage() {
                this.currentPage--;
                this.getOwners();
                window.scrollTo({top: 0, behavior: 'smooth'});
            },

            nextPage() {
                this.currentPage++;
                this.getOwners();
                window.scrollTo({top: 0, behavior: 'smooth'});
            },
        },
    })

    app.mount('#houseOwnerTable');
});

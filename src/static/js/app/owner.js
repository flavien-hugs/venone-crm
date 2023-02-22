window.addEventListener('DOMContentLoaded', event => {

    const DEFAULT_EDIT_DATA = {
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

    var app = Vue.createApp({
        data() {
            return {
                owners: [],
                owner: [],
                perPage: 20,
                currentPage: 1,
                totalPages: 1,
                ownerUUID: null,
                showDeleteAlert: false,
                isLoading: false,
                updateDataOwner: { ...DEFAULT_EDIT_DATA }
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
            getOwners() {
                this.isLoading = true
                const route = `{{ url_for('api.get_all_houseowners') }}`;

                fetch(`/api/owners/?page=` + this.currentPage, {
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
                    this.owners = data.houseowners;
                    this.totalPages = Math.ceil(data.total / this.perPage);
                })
                .catch((error) => console.error(error))
                .finally(() => {
                    this.isLoading = false;
                });
            },

            getOwner(ownerUUID) {
                const getOwnerURL = `/api/owner/${ownerUUID}/`;
                fetch(getOwnerURL, {
                    method: "GET",
                    headers: {'Content-type': 'application/json'},
                })
                .then(response => response.json())
                .then((data) => {
                    this.owner = data;
                    const modal = new bootstrap.Modal(document.getElementById('detailModal'));
                    modal.show();
                })
                .catch((error) => console.error(error));
            },

            deleteOwnerConfirm(ownerUUID) {
                this.ownerUUID = ownerUUID;
                const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
                modal.show();
            },

            onDeleteOwner() {
                const deleteURL = `/api/owner/${this.ownerUUID}/delete/`;
                fetch(deleteURL, {
                    method: "DELETE",
                    headers: {
                        'Content-type': 'application/json'
                    }
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        this.owners = this.owners.filter(owner => owner.owner_uuid !== this.ownerUUID);
                        this.getOwners();
                        this.ownerUUID = null;
                        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmModal'));
                        modal.hide();
                        this.showDeleteAlert = true;
                        setTimeout(() => {
                            this.showDeleteAlert = false;
                        }, 3000);
                    } else {
                        console.log(data.message);
                    }
                })
                .catch((error) => console.error(error));
            },

            updateOwnerConfirm(owner) {
                this.updateDataOwner = { ...owner } ?? {};
                const modal = new bootstrap.Modal(document.getElementById('editModal'));
                modal.show();
            },

            onUpdateOwner() {
                const updateURL = `/api/owner/${this.updateDataOwner.owner_uuid}/update/`;
                fetch(updateURL, {
                    method: "PUT",
                    headers: {'Content-type': 'application/json'},
                    body: JSON.stringify(this.updateDataOwner),
                })
                .then(response => response.json())
                .then((data) => {
                    if (data.success) {
                        const index = this.owners.findIndex(owner => owner.owner_uuid === this.updateDataOwner.owner_uuid);
                        this.owners.splice(index, 1, this.updateDataOwner);
                        this.updateDataOwner = { ...DEFAULT_EDIT_DATA };
                        this.getOwners();
                    } else {
                        console.log(data.message);
                    }
                })
                .catch((error) => console.error(error))
                .finally(() => {
                    this.updateDataOwner.owner_uuid = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                    modal.hide();
                });
            },

            prevPage() {
                if (this.currentPage > this.totalPages) {
                    this.currentPage--;
                    this.getOwners();
                }
                window.scrollTo({top: 0, behavior: 'smooth'});
            },

            nextPage() {
                if (this.currentPage <= this.totalPages) {
                    this.currentPage++;
                    this.getOwners();
                }
                window.scrollTo({top: 0, behavior: 'smooth'});
            },
        },
    });

    app.mount('#houseOwnerTable');
});

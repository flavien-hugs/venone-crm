window.addEventListener('DOMContentLoaded', event => {

    const HOUSE_DATA = {
        house_uuid: '',
        house_type: '',
        house_rent: '',
        house_guaranty: '',
        house_month: '',
        house_number_room: '',
        house_address: '',
    };

    var app = Vue.createApp({
        data() {
            return {
                houses: [],
                house: [],
                perPage: 10,
                currentPage: 1,
                totalPages: 1,
                isLoading: false,
                messageAlert: "",
                showMessageAlert: false,
                deleteHouseUUID: null,
                houseData: { ...HOUSE_DATA },
            }
        },
        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"]
        },

        mounted() {
            this.getHouses()
        },

        methods: {
            async getHouses() {
                try {
                    this.isLoading = true;
                    const houseURL = `/api/houses/?page=${this.currentPage}`;

                    const response = await fetch(houseURL, {
                        method: "GET",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        this.houses = data.houses;
                        this.totalPages = Math.ceil(data.total / this.perPage);
                        this.isLoading = false;
                    } else {
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                } catch (error) {
                    console.error("FETCH ERROR:", error);
                    this.houses = error;
                }
            },

            updateHouse(house) {
                this.houseData = { ...house } ?? {};
                const modal = new bootstrap.Modal(document.getElementById('updateHouseConfirm'));
                modal.show();
            },

            deleteHouseConfirm(houseUUID) {
                this.deleteHouseUUID = houseUUID;
                const modal = new bootstrap.Modal(document.getElementById('deleteHouseModal'));
                modal.show();
            },

            async onUpdateHouse() {
                try {
                    const updateURL = `/api/house/${this.houseData.house_uuid}/update/`;
                    const response = await fetch(updateURL, {
                        method: "PUT",
                        headers: {'Content-type': 'application/json'},
                        body: JSON.stringify(this.houseData),
                    });

                    const data = await response.json();

                    if (data.success) {
                        const index = this.houses.findIndex(house => house.house_uuid === this.houseData.house_uuid);
                        this.houses.splice(index, 1, this.houseData);
                        this.houseData = { ...HOUSE_DATA };
                        await this.getHouses();

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
                    this.houseData.house_uuid = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('updateHouseConfirm'));
                    modal.hide();
                }
            },

            async onDeleteHouse() {
                try {
                    const deleteURL = `/api/house/${this.deleteHouseUUID}/delete/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.houses = this.houses.filter(house => house.house_uuid !== this.deleteHouseUUID);
                        await this.getHouses();

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
                    this.deleteHouseUUID = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteHouseModal'));
                    modal.hide();
                }
            },

            prevPage() {
                this.currentPage--;
                this.getHouses();
                window.scrollTo({top: 0, behavior: 'smooth'});
            },

            nextPage() {
                this.currentPage++;
                this.getHouses();
                window.scrollTo({top: 0, behavior: 'smooth'});
            },
        },
    })

    app.mount('#houseTable');
});

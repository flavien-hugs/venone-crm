window.addEventListener('DOMContentLoaded', event => {
    var app = Vue.createApp({
        data() {
            return {
                houses: [],
                perPage: 20,
                currentPage: 1,
                totalPages: 1,
                isLoading: false,
                deleteHouseUUID: null,
                showDeleteAlert: false,
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
            getHouses() {

                this.isLoading = true
                const url = '{{ url_for("api.get_all_houses")|tojson }}';

                fetch(`/api/houses/?page=` + this.currentPage, {
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
                    this.houses = data.houses;
                    this.totalPages = Math.ceil(data.total / this.perPage);
                    this.isLoading = false;
                    console.log(data.houses);
                })
                .catch((error) => {
                    console.error("FETCH ERROR:", error);
                    this.houses = error;
                });
            },

            deleteHouseConfirm(houseUUID) {
                this.deleteHouseUUID = houseUUID;
                const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
                modal.show();
            },

            onDeleteHouse() {
                const deleteURL = `/api/house/${this.deleteHouseUUID}/delete/`;
                fetch(deleteURL, {
                    method: "DELETE",
                    headers: {
                        'Content-type': 'application/json'
                    }
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        this.houses = this.houses.filter(house => house.house_uuid !== this.deleteHouseUUID);
                        this.getHouses();
                        this.deleteHouseUUID = null;
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
                    this.getHouses();
                }
                window.scrollTo({top: 0, behavior: 'smooth'});
            },

            nextPage() {
                if (this.currentPage <= this.totalPages) {
                    this.currentPage++;
                    this.getHouses();
                }
                window.scrollTo({top: 0, behavior: 'smooth'});
            },
        },
    })

    app.mount('#houseTable');
});

import paginateComponent from './components/paginateComponent.js';
import messageComponent from './components/messageComponent.js';

window.addEventListener('DOMContentLoaded', event => {

    const HOUSE_DATA = {
        house_uuid: '',
        house_type: '',
        house_rent: '',
        house_guaranty: '',
        house_month: '',
        house_number_room: '',
        house_address: '',
        lease_start_date: '',
    }

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
                house: [],
                houses: [],
                houseUUID: null,

                perPage: 10,
                currentPage: 1,
                currentStep: 1,
                totalPages: 1,
                isLoading: false,
                messageAlert: "",
                showMessageAlert: false,
                deleteHouseUUID: null,
                houseData: { ...HOUSE_DATA },
                tenantData: { ...TENANT_DATA },
            };
        },

        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"],
        },

        async mounted() {
            await this.getHouses();
        },

        methods: {

            downloadHouseCSV() {
                window.location.href = `/dashboard/export-houses-data`;
            },

            nextStep() {
                this.currentStep++;
            },

            prevStep() {
                this.currentStep--;
            },

            calculateGuaranty() {
                const hrent = parseInt(this.houseData.house_rent);
                const hmonth = parseInt(this.houseData.house_month);
                if (!isNaN(hrent) && !isNaN(hmonth))
                    return (this.houseData.house_guaranty = hrent * hmonth);
                else {
                    return;
                }
            },

            async getHouses() {
                try {
                    this.isLoading = true;
                    const houseURL = `/api/houses/?page=${this.currentPage}`;

                    const response = await fetch(houseURL, {
                        method: "GET",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    if (response.status == 200) {
                        this.isLoading = false;
                        const data = await response.json();
                        this.houses = data.houses;
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

            updateHouse(house) {
                this.houseData = { ...house } ?? {};
                const modal = new bootstrap.Modal(
                    document.getElementById("updateHouseConfirm")
                );
                modal.show();
            },

            assignHouseToTenantConfirm(houseUuid) {
                this.houseUUID = houseUuid;
                this.houseData = { ...houseUuid };
                this.tenantData = { ...houseUuid };
                const modal = new bootstrap.Modal(
                    document.getElementById("assignHouseToTenantModal")
                );
                modal.show();
            },

            deleteHouseConfirm(houseUUID) {
                this.deleteHouseUUID = houseUUID;
                const modal = new bootstrap.Modal(
                    document.getElementById("deleteHouseModal")
                );
                modal.show();
            },

            async onUpdateHouse() {
                try {
                    const updateURL = `/api/house/${this.houseData.house_uuid}/update/`;
                    const response = await fetch(updateURL, {
                        method: "PUT",
                        headers: { "Content-type": "application/json" },
                        body: JSON.stringify(this.houseData),
                    });

                    const data = await response.json();

                    if (data.success) {
                        const index = this.houses.findIndex(
                            (house) =>
                                house.house_uuid === this.houseData.house_uuid
                        );
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
                    console.error("FETCH ERROR:", error);
                    this.showMessageAlert = true;
                    this.messageAlert =
                        "Une erreur est survenue lors de la mise à jour de cette propriété";
                } finally {
                    this.houseData.house_uuid = null;
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("updateHouseConfirm")
                    );
                    modal.hide();
                }
            },

            async onDeleteHouse() {
                try {
                    const deleteURL = `/api/house/${this.deleteHouseUUID}/delete/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.houses = this.houses.filter(
                            (house) => house.house_uuid !== this.deleteHouseUUID
                        );
                        await this.getHouses();

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
                        "Une erreur est survenue lors de la suppression de cette propriété";
                } finally {
                    this.deleteHouseUUID = null;
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("deleteHouseModal")
                    );
                    modal.hide();
                }
            },

            async onAssignHouseToTenant() {
                try {
                    const assignURL = `/api/house/${this.houseData.house_uuid}/house_assign_tenant/`;
                    const response = await fetch(assignURL, {
                        method: "PATCH",
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
                        this.tenantData = { ...TENANT_DATA };
                        this.houseData = { ...HOUSE_DATA };
                        await this.getHouses();

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
                        "Une erreur est survenue lors de la mise en location.";
                } finally {
                    const modelElement = document.getElementById(
                        "assignHouseToTenantModal"
                    );
                    const modal = bootstrap.Modal.getInstance(modelElement);
                    modal.hide();
                }
            },

            prevPage() {
                this.currentPage--;
                this.getHouses();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },

            nextPage() {
                this.currentPage++;
                this.getHouses();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },
        },
    });

    app.mount("#houseApp");
});

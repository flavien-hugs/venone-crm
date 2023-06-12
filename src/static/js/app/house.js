import paginateComponent from './components/paginateComponent.js';
import messageComponent from './components/messageComponent.js';

window.addEventListener('DOMContentLoaded', event => {
    const HOUSE_DATA = {
        uuid: '',
        vn_house_id: '',
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
                house: [],
                houses: [],
                houseUUID: null,

                currentPage: 1,
                currentStep: 1,
                totalPages: 1,
                isLoading: false,
                messageAlert: "",
                showMessageAlert: false,
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
                const hrent = parseFloat(this.houseData.vn_house_rent);
                const hmonth = parseInt(this.houseData.vn_house_month);

                if (!isNaN(hrent) && !isNaN(hmonth)) {
                    return hrent * hmonth;
                } else {
                    return null;
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

            createHouse() {
                const modal = new bootstrap.Modal(document.getElementById('createHouseModal'));
                modal.show();
            },

            updateHouse(house) {
                this.houseData = { ...house } ?? {};
                const modal = new bootstrap.Modal(
                    document.getElementById("updateHouseConfirm")
                );
                modal.show();
            },

            assignHouseToTenantConfirm(houseUUID) {
                this.houseUUID = houseUUID;
                this.houseData = { ...houseUUID };
                this.tenantData = { ...houseUUID };
                const modal = new bootstrap.Modal(
                    document.getElementById("assignHouseToTenantModal")
                );
                modal.show();
            },

            deleteHouseConfirm(houseUUID) {
                this.houseUUID = houseUUID;
                const modal = new bootstrap.Modal(
                    document.getElementById("deleteHouseModal")
                );
                modal.show();
            },

            async onCreateHouse() {
                try {
                    const houseRegisterURL = `/api/houses/`;
                    const response = await fetch(houseRegisterURL, {
                        method: "POST",
                        headers: {
                            'Content-type': 'application/json'
                        },
                        body: JSON.stringify({
                            create_house_data: this.houseData,
                        }),
                    });

                    const data = await response.json();

                    if (data.success) {
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
                    console.log(error);
                    this.showMessageAlert = true;
                    this.messageAlert = "Une erreur est survenue lors de l'enregistrement.";
                } finally {
                    this.houseData.uuid = null;
                    const modal = bootstrap.Modal.getInstance(document.getElementById('createHouseModal'));
                    modal.hide();
                }
            },

            async onUpdateHouse() {
                try {
                    const updateURL = `/api/houses/${this.houseData.uuid}/`;
                    const response = await fetch(updateURL, {
                        method: "PATCH",
                        headers: { "Content-type": "application/json" },
                        body: JSON.stringify(this.houseData),
                    });

                    const { success, message } = await response.json();

                    if (success) {
                        const houseUUID = this.houseData.uuid;
                        const houseIndex = this.houses.findIndex(
                            (house) => house.uuid === houseUUID
                        );
                        this.houses.splice(houseIndex, 1, this.houseData);
                        this.houseData = { ...HOUSE_DATA };
                        await this.getHouses();

                        this.showMessageAlert = true;
                        this.messageAlert = message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                            this.messageAlert = message;
                        }, 3000);
                    } else {
                        this.messageAlert = message;
                    }
                } catch (error) {
                    console.error("FETCH ERROR:", error);
                    this.showMessageAlert = true;
                    this.messageAlert =
                        "Une erreur est survenue lors de la mise à jour de cette propriété";
                } finally {
                    this.houseData.uuid = null;
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("updateHouseConfirm")
                    );
                    modal.hide();
                }
            },

            async onDeleteHouse() {
                try {
                    const deleteURL = `/api/houses/${this.houseUUID}/`;
                    const response = await fetch(deleteURL, {
                        method: "DELETE",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.houses = this.houses.filter(
                            (house) => house.uuid !== this.houseUUID
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
                    this.houseUUID = null;
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("deleteHouseModal")
                    );
                    modal.hide();
                }
            },

            async onAssignHouseToTenant() {
                try {
                    const assignURL = `/api/houses/${this.houseData.uuid}/house-assign-tenant/`;
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

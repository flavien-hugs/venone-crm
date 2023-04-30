import paginateComponent from "./components/paginateComponent.js";
import messageComponent from "./components/messageComponent.js";

window.addEventListener("DOMContentLoaded", (event) => {

    const TRANSFER_DATA = {
        trans_amount: "",
        withdrawal_number: "",
    };

    var app = Vue.createApp({
        components: {
            paginateComponent,
            messageComponent,
        },

        data() {
            return {
                user: [],
                transfers: [],

                perPage: 10,
                currentPage: 1,
                totalPages: 1,
                isLoading: false,
                messageAlert: "",
                showMessageAlert: false,

                searchQuery: "",
                transferData: { ...TRANSFER_DATA },
            };
        },

        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"],
        },

        async mounted() {
            await this.getTransfers();
        },

        watch: {
            "transferData.trans_amount": function (f) {
                this.transferData.trans_amount = this.filterNumber(f);
            },
            "transferData.withdrawal_number": function (f) {
                this.transferData.withdrawal_number = this.filterNumber(f);
            },
        },

        computed: {
            isFormValid() {
                return (
                    this.transferData.trans_amount !== "" &&
                    this.transferData.withdrawal_number !== ""
                );
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
                return ("" + e).replace(/[^0-9]/g, "");
            },

            async getTransfers() {
                try {
                    this.isLoading = true;
                    const transferRequestURL = `/api/transfers-request/?page=${this.currentPage}`;

                    const response = await fetch(transferRequestURL, {
                        method: "GET",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    if (response.status == 200) {
                        this.isLoading = false;
                        const data = await response.json();
                        this.transfers = data.transfers;
                        this.user = data.user;
                        this.totalPages = Math.ceil(data.total / this.perPage);
                        this.currentPage = data.page;
                    } else {
                        this.isLoading = false;
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                } catch (error) {
                    this.showMessageAlert = true;
                    this.messageAlert =
                        "Oops, problème de connexion au serveur.";
                }
            },

            createTransferRequest() {
                const modal = new bootstrap.Modal(
                    document.getElementById("createTransferRequestModal")
                );
                modal.show();
            },

            async onCreateTransferRequest() {
                try {
                    const createRequestURL = `/api/transfers-request/create/`;

                    this.transferData.trans_amount = parseFloat(
                        this.transferData.trans_amount
                    );

                    const response = await fetch(createRequestURL, {
                        method: "POST",
                        headers: {
                            "Content-type": "application/json",
                        },
                        body: JSON.stringify({
                            transfer_data: this.transferData,
                        }),
                    });

                    const data = await response.json();

                    if (data.success) {
                        await this.getTransfers();
                        this.transferData = { ...TRANSFER_DATA };
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    }
                } catch (error) {
                    console.log(error);
                    this.showMessageAlert = true;
                    this.messageAlert = "Oops ! Une erreur est survenue";
                } finally {
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("createTransferRequestModal")
                    );
                    modal.hide();
                }
            },

            prevPage() {
                this.currentPage--;
                this.getTransfers();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },

            nextPage() {
                this.currentPage++;
                this.getTransfers();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },
        },
    });

    app.mount("#requestTransferTable");
});

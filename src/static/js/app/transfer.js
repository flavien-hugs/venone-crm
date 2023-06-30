import paginateComponent from "./components/paginateComponent.js";
import messageComponent from "./components/messageComponent.js";

window.addEventListener("DOMContentLoaded", (event) => {

    const TRANSFER_DATA = {
        vn_trans_amount: "",
        vn_withdrawal_number: "",
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
            "transferData.vn_trans_amount": function (f) {
                this.transferData.vn_trans_amount = this.filterNumber(f);
            },
            "transferData.withdrawal_number": function (f) {
                this.transferData.vn_withdrawal_number = this.filterNumber(f);
            },
        },

        computed: {
            isFormValid() {
                return (
                    this.transferData.vn_trans_amount !== "" &&
                    this.transferData.vn_withdrawal_number !== ""
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
                    const transferRequestURL = `/api/transfers/?page=${this.currentPage}`;

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
                        this.totalPages = Math.ceil(data.total / data.per_page);
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
                    const createRequestURL = `/api/transfers/`;

                    this.transferData.vn_trans_amount = parseFloat(
                        this.transferData.vn_trans_amount
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

                    const { success, message } = await response.json();

                    if (success) {
                        await this.getTransfers();
                        this.transferData = { ...TRANSFER_DATA };
                        this.showMessageAlert = true;
                        this.messageAlert = message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    }
                } catch (error) {
                    console.error(error);
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

import paginateComponent from "./components/paginateComponent.js";
import messageComponent from "./components/messageComponent.js";

window.addEventListener("DOMContentLoaded", (event) => {

    var app = Vue.createApp({
        components: {
            paginateComponent,
            messageComponent,
        },

        data() {
            return {
                user: [],
                payments: [],

                currentPage: 1,
                totalPages: 1,
                isLoading: false,
                messageAlert: "",
                showMessageAlert: false,

                searchQuery: "",
            };
        },

        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"],
        },

        async mounted() {
            await this.getPayments();
        },

        methods: {

            downloadPaymentCSV() {
                window.location.href = `/dashboard/export-payments-data`;
            },

            async getPayments() {
                try {
                    this.isLoading = true;
                    const paymentURL = `/api/payments/?page=${this.currentPage}`;

                    const response = await fetch(paymentURL, {
                        method: "GET",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    if (response.ok) {
                        this.isLoading = false;
                        const data = await response.json();
                        this.payments = data.payments;
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

            prevPage() {
                this.currentPage--;
                this.getPayments();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },

            nextPage() {
                this.currentPage++;
                this.getPayments();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },
        },
    });

    app.mount("#checkoutTable");
});

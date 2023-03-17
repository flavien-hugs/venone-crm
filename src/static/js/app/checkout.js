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
                houses: [],

                perPage: 10,
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
            await this.getHouses();
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
                        this.isLoading = false;
                        const data = await response.json();
                        console.log(data)
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
                    this.showMessageAlert = true;
                    this.messageAlert = 'Oops, problème de connexion au serveur.';
                }
            },

            prevPage() {
                this.currentPage--;
                this.getTenants();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },

            nextPage() {
                this.currentPage++;
                this.getTenants();
                window.scrollTo({ top: 0, behavior: "smooth" });
            },
        },
    });

    app.mount("#checkoutTable");
});

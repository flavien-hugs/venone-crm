import paginateComponent from './components/paginateComponent.js';
import messageComponent from "./components/messageComponent.js";

var app = Vue.createApp({
    components: {
        paginateComponent,
        messageComponent,
    },

    data() {
        return {
            houses: [],

            perPage: 10,
            currentPage: 1,
            currentStep: 1,
            totalPages: 1,
            isLoading: false,
            messageAlert: "",
            showMessageAlert: false,
        };
    },

    delimiters: ["{", "}"],
    compilerOptions: {
        delimiters: ["{", "}"],
    },

    async mounted() {
        await this.getFindHouses();
    },

    methods: {
        nextStep() {
            this.currentStep++;
        },

        prevStep() {
            this.currentStep--;
        },

        async getFindHouses() {
            try {
                this.isLoading = true;
                const checkHousesURL = `/api/check-houses-country/?page=${this.currentPage}`;

                const response = await fetch(checkHousesURL, {
                    method: "GET",
                    headers: {
                        "Content-type": "application/json",
                    },
                });

                if (response.status == 200) {
                    this.isLoading = false;
                    const data = await response.json();
                    this.houses = data.houses;
                    this.totalPages = Math.ceil(data.total / this.perPage);
                    this.currentPage = data.page;
                } else {
                    this.isLoading = false;
                    throw new Error("NETWORK RESPONSE ERROR");
                }
            } catch (error) {
                this.showMessageAlert = true;
                this.messageAlert = "Oops, problème de connexion au serveur.";
            }
        },

        prevPage() {
            this.currentPage--;
            this.getFindHouses();
            window.scrollTo({ top: 0, behavior: "smooth" });
        },

        nextPage() {
            this.currentPage++;
            this.getFindHouses();
            window.scrollTo({ top: 0, behavior: "smooth" });
        },
    },
});

app.mount("#othersHousesApp");

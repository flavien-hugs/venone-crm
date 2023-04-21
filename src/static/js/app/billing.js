import messageComponent from "./components/messageComponent.js";

window.addEventListener("DOMContentLoaded", (event) => {
    var app = Vue.createApp({

        components: {
            messageComponent,
        },

        data() {
            return {
                user: [],
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
            await this.getUser();
        },

        methods: {
            filterNumber(e) {
                return  ("" + e).replace(/[^0-9]/g, '');
            },

            async getUser() {
                try {
                    this.isLoading = true;
                    const userURL = `/api/user/`;

                    const response = await fetch(userURL, {
                        method: "GET",
                        headers: {
                            "Content-type": "application/json",
                        },
                    });

                    if (response.status == 200) {
                        this.isLoading = false;
                        const data = await response.json();
                        this.user = data.user;
                    } else {
                        this.isLoading = false;
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                } catch (error) {
                    this.showMessageAlert = true;
                    this.messageAlert = 'Oops, problème de connexion au serveur.';
                }
            },
        },
    });

    app.mount("#billingApp");
});

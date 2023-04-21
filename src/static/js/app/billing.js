import messageComponent from "./components/messageComponent.js";

window.addEventListener("DOMContentLoaded", (event) => {
    var app = Vue.createApp({

        components: {
            messageComponent,
        },

        data() {
            return {
                user: [],
                percent: '',
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

        watch: {
            'percent': function (f){
                this.percent = this.filterNumber(f);
            },
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

            async onUpdatePercent() {
                try {
                    const percentApplyURL = `/api/define-percent/`;

                    if (
                        this.percent === "" ||
                        isNaN(this.percent) ||
                        this.percent < 0 ||
                        this.percent > 100
                    ) {
                        this.showMessageAlert = true;
                        this.messageAlert = "Valeur de pourcentage invalide. Le pourcentage doit être un nombre entre 0 et 100.";
                        return;
                    }

                    const response = await fetch(percentApplyURL, {
                        method: "PATCH",
                        headers: {
                            "Content-type": "application/json",
                        },
                        body: JSON.stringify({
                            percent: parseFloat(this.percent),
                        }),
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.showMessageAlert = true;
                        this.messageAlert = data.message;
                        setTimeout(() => {
                            this.showMessageAlert = false;
                        }, 3000);
                    } else {
                        this.showMessageAlert = true;
                        this.messageAlert = "Oops !, un problème est survenu lors de l'enregistrement.";
                    }
                } catch (error) {
                    this.showMessageAlert = true;
                    this.messageAlert = "Oops, problème de connexion au serveur.";
                }
            },
        },

        computed: {
            percentValue() {
                return this.percent !== "" ? parseFloat(this.percent) : 0;
            },
        },
    });

    app.mount("#billingApp");
});

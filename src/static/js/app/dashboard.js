window.addEventListener('DOMContentLoaded', event => {
    var app = Vue.createApp({
        data() {
            return {
                user: [],
                isLoading: false,
            }
        },
        delimiters: ["{", "}"],
        compilerOptions: {
            delimiters: ["{", "}"]
        },

        mounted() {
            this.getUser()
        },

        methods: {
            async getUser() {
                try {
                    this.isLoading = true;
                    const userURL = `/api/user/`;

                    const response = await fetch(userURL, {
                        method: "GET",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        console.log(data.user)
                        this.user = data.user;
                        this.isLoading = false;
                    } else {
                        throw new Error("NETWORK RESPONSE ERROR");
                    }
                } catch (error) {
                    console.error("FETCH ERROR:", error);
                    this.houses = error;
                }
            },
        },
    })

    app.mount('#dashboardComponent');
});

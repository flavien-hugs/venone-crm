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
                tenants: [],

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

        watch: {
            searchQuery: function() {
                this.filteredTenants;
            }
        },

        computed: {
            filteredTenants() {
                if (!this.searchQuery) {
                    return this.tenants;
                }

                const searchRegex = new RegExp(this.searchQuery, 'i');

                    return this.tenants.filter(tenant => {
                        const fullnameMatch = searchRegex.test(tenant.fullname);
                        const addrEmailMatch = searchRegex.test(tenant.addr_email);
                        const phonenumberOneMatch = searchRegex.test(tenant.phonenumber_one);
                        const phonenumberTwoMatch = searchRegex.test(tenant.phonenumber_two);
                        const cardNumberMatch = searchRegex.test(tenant.card_number);

                    return (
                        fullnameMatch ||
                        addrEmailMatch ||
                        phonenumberOneMatch ||
                        phonenumberTwoMatch ||
                        cardNumberMatch
                    );
                });
            },
        },

        async mounted() {
            await this.getTenants();
        },

        methods: {
            async getTenants() {
                try {
                    this.isLoading = true;
                    const tenantURL = `/api/tenants/?page=${this.currentPage}&per_page=${this.perPage}&q=${this.searchQuery}`;

                    const response = await fetch(tenantURL, {
                        method: "GET",
                        headers: {
                            'Content-type': 'application/json'
                        }
                    });

                    this.isLoading = false;

                    if (response.status == 200) {
                        const data = await response.json();
                        this.tenants = data.tenants;
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

import KpiComponent from './components/kpiComponent.js';

const months = Array.from({ length: 12 }, (_, i) => {
    const date = new Date();
    date.setMonth(i);
    return date.toLocaleString('default', { month: 'short' });
});

var app = Vue.createApp({
    components: {
        "kpi-component": KpiComponent,
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

        await this.getOwnerData();
        await this.getTenantData();
        await this.getOpenHousesData();
        await this.getTrendPriceData();
    },

    methods: {
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

                this.isLoading = false;

                if (response.status == 200) {
                    const data = await response.json();
                    this.user = data.user;
                } else {
                    this.isLoading = false;
                    console.log(error);
                }
            } catch (error) {
                console.log("FETCH ERROR:", error);
                this.showMessageAlert = true;
                this.messageAlert = 'Oops, problème de connexion au serveur.';
            }
        },

        async getOwnerData() {
            try {
                const ownerDataURL = `/api/owners/data/`;

                const response = await fetch(ownerDataURL, {
                    method: "GET",
                    headers: {
                        "Content-type": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    const values = data.map((d) => d.count);

                    const ctx = document
                        .getElementById("ownerChart")
                        .getContext("2d");
                    const chart = new Chart(ctx, {
                        type: "bar",
                        data: {
                            labels: months,
                            datasets: [
                                {
                                    data: values,
                                    backgroundColor: "rgba(0, 97, 242, 1)",
                                    hoverBackgroundColor:
                                        "rgba(0, 97, 242, 0.9)",
                                    borderColor: "#4e73df",
                                    borderWidth: 1,
                                    maxBarThickness: 25,
                                },
                            ],
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                yAxes: [
                                    {
                                        ticks: {
                                            beginAtZero: true,
                                        },
                                    },
                                ],
                            },
                            legend: {
                                display: false,
                            },
                        },
                    });
                } else {
                    throw new Error("NETWORK RESPONSE ERROR");
                }
            } catch (error) {
                console.error("FETCH ERROR:", error);
                this.showMessageAlert = true;
                this.messageAlert = 'Oops, problème de connexion au serveur.';
            }
        },

        async getTenantData() {
            try {
                const tenantDataURL = `/api/tenants/data/`;

                const response = await fetch(tenantDataURL, {
                    method: "GET",
                    headers: {
                        "Content-type": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    const values = data.map((d) => d.count);

                    const ctx = document
                        .getElementById("tenantChart")
                        .getContext("2d");
                    const chart = new Chart(ctx, {
                        type: "bar",
                        data: {
                            labels: months,
                            datasets: [
                                {
                                    data: values,
                                    backgroundColor: "rgba(0, 97, 242, 1)",
                                    hoverBackgroundColor: "rgba(0, 97, 242, 0.9)",
                                    borderColor: "#4e73df",
                                    borderWidth: 1,
                                    maxBarThickness: 25,
                                },
                            ],
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                yAxes: [
                                    {
                                        ticks: {
                                            beginAtZero: true,
                                        },
                                    },
                                ],
                            },
                            legend: {
                                display: false,
                            },
                        },
                    });
                } else {
                    throw new Error("NETWORK RESPONSE ERROR");
                }
            } catch (error) {
                console.error("FETCH ERROR:", error);
                this.showMessageAlert = true;
                this.messageAlert = 'Oops, problème de connexion au serveur.';
            }
        },

        async getOpenHousesData() {
            try {
                const houseOpenDataURL = `/api/available_properties/data/`;

                const response = await fetch(houseOpenDataURL, {
                    method: "GET",
                    headers: {
                        "Content-type": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();

                    const notOpenValues = data.map((d) => d.notOpen);
                    const isOpenValues = data.map((d) => d.isOpen);

                    const ctx = document.getElementById("openHouseChart");

                    const chart = new Chart(ctx, {
                        type: "pie",
                        data: {
                            labels: ["Disponible", "Indisponible"],
                            datasets: [
                                {
                                    data: [notOpenValues , isOpenValues],
                                    backgroundColor: [
                                        "rgba(0, 97, 242, 1)",
                                        "rgba(0, 172, 105, 1)",
                                    ],
                                    hoverOffset: 4
                                },
                            ],
                        },
                        options: {
                            responsive: true,
                            scales: {
                                r: {
                                    pointLabels: {
                                        display: true,
                                        centerPointLables: true,
                                        font: {
                                            size: 18
                                        }
                                    }
                                }
                            },
                        },
                    });
                } else {
                    throw new Error("NETWORK RESPONSE ERROR");
                }
            } catch (error) {
                console.error("FETCH ERROR:", error);
                this.showMessageAlert = true;
                this.messageAlert = 'Oops, problème de connexion au serveur.';
            }
        },

        async getTrendPriceData() {
            try {
                const trendPriceDataURL = `/api/trendprices/data/`;

                const response = await fetch(trendPriceDataURL, {
                    method: "GET",
                    headers: {
                        "Content-type": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();

                    const prices = data.map(d => d.price);

                    const ctx = document.getElementById("trendPriceChart");

                    const chart = new Chart(ctx, {
                        type: "line",
                        data: {
                            labels: months,
                            datasets: [
                                {
                                    data: prices,
                                    fill: false,
                                    borderColor: "rgb(75, 192, 192)",
                                    tension: 0.1,
                                    lineTension: 0.1
                                },
                            ],
                        },
                        options: {
                            scales: {
                                yAxes: [
                                    {
                                        ticks: {
                                            beginAtZero: true,
                                        },
                                    },
                                ],
                            },
                            legend: {
                                display: false,
                            },
                        },
                    });
                } else {
                    throw new Error("NETWORK RESPONSE ERROR");
                }
            } catch (error) {
                console.error("FETCH ERROR:", error);
                this.showMessageAlert = true;
                this.messageAlert = 'Oops, problème de connexion au serveur.';
            }
        },
    },
});

app.mount('#dashboardApp');

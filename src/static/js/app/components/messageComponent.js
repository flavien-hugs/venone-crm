const messageComponent = {

	props: [
        "messageAlert",
		"showMessageAlert",
	],

	template: `
		<div v-if="showMessageAlert" class="alert alert-success" role="alert">
            {{ messageAlert }}
        </div>
	`
};

export default messageComponent

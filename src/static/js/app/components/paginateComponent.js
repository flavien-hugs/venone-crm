const paginateComponent = {

	props: [
		"currentPage",
        "totalPages",
        "prevPage",
        "nextPage",
	],

	template: `
		<nav v-if="totalPages > 1" class="my-2">
			<ul class="pagination justify-content-center text-center">
				<li class="page-item" :class="[currentPage <= 1 ? 'disabled' : '']">
					<a type="button" class="page-link small" @click.prevent="prevPage">
					<i class="me-2" data-feather="chevron-left"></i>Précédent</a>
				</li>

				<li class="page-item">
					<span class="page-link small">{{ currentPage }} - {{ totalPages }}</span>
		        </li>

				<li class="page-item" :class="[currentPage >= totalPages ? 'disabled' : '']">
					<a type="button" class="page-link small" @click.prevent="nextPage">
					Suivant <i class="ms-2" data-feather="chevron-right"></i></a>
				</li>
			</ul>
		</nav>
	`
};

export default paginateComponent

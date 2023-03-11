const houseComponent = {
	
	props: {
	    houses: {
	    	type: Array,
	    	required: true,
	    },
	    updateHouse: {
	    	type: Function,
	    	required: true,
	    },
	    deleteHouseConfirm: {
	    	type: Function,
	    	required: true,
	    },
  	},
	
	template: `
		<table class="table table-hover">
			<thead class="small">
				<tr>
					<th scope="col">ID</th>
					<th scope="col">Proprité &amp; Localisation</th>
					<th scope="col">Loyer/mois</th>
					<th scope="col">Date mise en location</th>
					<th scope="col">Status location</th>
					<th>Actions</th>
				</tr>
			</thead>

			<tbody>
				<tr v-for="house in houses" :key="house.house_uuid">
					<td>
						<a href="#" class="badge bg-blue-soft text-blue">{{ house.house_id }}</a>
					</td>
					<td>
						{{ house.house_type }} <br>
						<small>{{ house.house_address }}</small>
					</td>
					<td>{{ house.house_rent.toLocaleString() }} {{  house.user.devise }}</td>
					<td>{{ house.house_lease_start_date.toLocaleString() }}</td>
					<td><span class="badge bg-danger text-white p-2">{{ house.house_status }}</span></td>
					<td>
						<button @click="updateHouse(house)" class="btn btn-datatable btn-icon btn-transparent-secondary me-2">
							<i class="fa fa-edit text-primary"></i>
						</button>

						<button @click="deleteHouseConfirm(house.house_uuid)" class="btn btn-datatable btn-icon btn-transparent-danger">
							<i class="fa fa-trash text-danger"></i>
						</button>
					</td>
				</tr>
			</tbody>
		</table>
	`,
};

export default houseComponent

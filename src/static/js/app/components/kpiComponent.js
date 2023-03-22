const KpiComponent = {
	props: ['user'],

	template: `
		<div class="row">
			<div :class="{ 'col-xl-4': user.is_owner, 'col-xl-3': user.is_company }" class="col-md-6 mb-4">
				<div class="card border-start-lg border-start-primary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary mb-2 text-uppercase">solde actuel</div>
								<div class="h1">{{ user.total_payment_month }} {{ user.devise }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-dollar-sign fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div :class="{ 'col-xl-4': user.is_owner, 'col-xl-3': user.is_company }" class="col-md-6 mb-4">
				<div class="card border-start-lg border-start-success h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-success text-uppercase mb-2">nombre de locataires</div>
								<div class="h1">{{ user.tenant_count }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-users fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div v-if="user.is_company" class="col-xl-3 col-md-6 mb-4">
				<div class="card border-start-lg border-start-info h-100 jut">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-info mb-2 text-uppercase">nombre de bailleurs</div>
								<div class="h1">{{ user.owner_count }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-users fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div :class="{ 'col-xl-4': user.is_owner, 'col-xl-3': user.is_company }" class="col-md-6 mb-4">
				<div class="card border-start-lg border-start-secondary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-secondary mb-2 text-uppercase">nombre de propriétés</div>
								<div class="h1">{{ user.house_count }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-home fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>
		</div>
	`
};

export default KpiComponent

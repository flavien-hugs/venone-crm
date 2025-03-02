const KpiComponent = {
    props: ["user"],

    template: `
		<div class="row g-2">
			<div :class="{ 'col-xl-3': user.vn_house_owner, 'col-xl-3': user.is_company }" class="col-xl-3 mb-4">
				<div class="card border-start-lg border-start-primary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary mb-2 text-uppercase">solde</div>
								<div class="h1 fw-700">{{ user.total_payments_received }} {{ user.vn_device }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-dollar-sign fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div :class="{ 'col-xl-3': user.vn_house_owner, 'col-xl-3': user.vn_company }" class="col-xl-3 mb-4">
				<div class="card border-start-lg border-start-primary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary mb-2 text-uppercase">total paiement reçu ce mois</div>
								<div class="h1 fw-700">{{ user.total_payment_month }} {{ user.vn_device }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-dollar-sign fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div :class="{ 'col-xl-3': user.vn_house_owner, 'col-xl-3': user.vn_company }" class="col-xl-3 mb-4">
				<div class="card border-start-lg border-start-primary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary mb-2 text-uppercase">total loyer à collecter</div>
								<div class="h1 fw-700">{{ user.total_house_amount }} {{ user.vn_device }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-dollar-sign fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div v-if="user.vn_company" class="col-xl-3 mb-4">
				<div class="card border-start-lg border-start-primary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary mb-2 text-uppercase">gains sur loyers à collectés</div>
								<div class="h1 fw-700">{{ user.total_house_percent }} {{ user.vn_device }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-dollar-sign fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div :class="{ 'col-xl-3': user.vn_house_owner, 'col-xl-3': user.vn_company }" class="col-xl-3 mb-4">
				<div class="card border-start-lg border-start-primary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary text-uppercase mb-2">total locataires</div>
								<div class="h1 fw-700">{{ user.tenants_count }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-users fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div v-if="user.vn_company" class="col-xl-3 mb-4">
				<div class="card border-start-lg border-start-primary h-100 jut">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary mb-2 text-uppercase">total bailleurs</div>
								<div class="h1 fw-700">{{ user.owners_count }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-users fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>

			<div :class="{ 'col-xl-3': user.vn_house_owner, 'col-xl-3': user.vn_company }" class="col-xl-3 mb-4">
				<div class="card border-start-lg border-start-primary h-100">
					<div class="card-body">
						<div class="d-flex align-items-center">
							<div class="flex-grow-1">
								<div class="small fw-bold text-primary mb-2 text-uppercase">total propriétés</div>
								<div class="h1 fw-700">{{ user.houses_count }}</div>
							</div>
							<div class="ms-2"><i class="fas fa-home fa-2x text-gray-200"></i></div>
						</div>
					</div>
				</div>
			</div>
		</div>
	`,
};

export default KpiComponent

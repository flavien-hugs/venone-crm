from flask import jsonify, request, current_app, url_for
from flask_login import login_required, current_user

from . import api
from src.tenant import VNHouse


@api.get('/houses/')
@login_required
def get_all_houses():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = VNHouse.get_houses_list()\
        .paginate(page=page, per_page=per_page, error_out=False)

    houses = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_all_houses', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_all_houses', page=page+1, _external=True)

    return jsonify(
        {
            'houses': [house.to_json() for house in houses],
            'prev': prev,
            'next': next,
            'page': page,
            'per_page': per_page,
            'total': pagination.total
        }
    )


@api.get('/house/<string:uuid>/')
@login_required
def get_house(uuid):
    house = VNHouse.get_house(uuid)
    return jsonify(house.to_json())


@api.delete('/house/<string:house_uuid>/delete/')
@login_required
def delete_house(house_uuid):
    house = VNHouse.get_house(house_uuid)
    if house is not None:
        house.delete()
        return jsonify({'success': True, 'message': f"Propriété {house} retirée avec succès."})
    return jsonify({'success': False, 'message': f"L'élément avec l'id {house_uuid} n'a pas été trouvé."})


@api.route('/house/<string:uuid>/tenant/')
@login_required
def get_house_tenant(uuid):
    house = VNHouse.get_house(uuid)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = house.tenants\
        .paginate(page=page, per_page=per_page, error_out=False)

    tenants = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_house_tenant', uuid=uuid, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_house_tenant', uuid=uuid, page=page+1, _external=True)

    return jsonify({
        'houses': [tenant.to_json() for tenant in tenants],
        'prev': prev,
        'next': next,
        'page': page,
        'per_page': per_page,
        'total': pagination.total
    })

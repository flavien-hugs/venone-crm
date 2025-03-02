import csv
import io


def generate_tenant_csv(data, headers):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)

    for row in data:
        writer.writerow(
            [
                row.vn_tenant_id,
                row.vn_fullname,
                row.vn_phonenumber_one,
                row.vn_addr_email,
                row.vn_cni_number,
                row.vn_profession,
                row.house.vn_house_rent,
                row.vn_created_at,
            ]
        )

    return output.getvalue()


def generate_owner_csv(data, headers):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)

    for row in data:
        writer.writerow(
            [
                row.vn_owner_id,
                row.vn_fullname,
                row.vn_phonenumber_one,
                row.vn_addr_email,
                row.vn_cni_number,
                row.vn_profession,
                row.get_tenants_count(),
                row.vn_created_at,
            ]
        )

    return output.getvalue()


def generate_house_csv(data, headers):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)

    for row in data:
        writer.writerow(
            [
                row.vn_house_id,
                row.owner.vn_fullname,
                row.vn_house_type,
                row.vn_house_rent,
                row.vn_house_guaranty,
                row.vn_house_number_room,
                row.vn_house_address,
                row.vn_house_lease_start_date,
                row.get_house_open(),
                row.vn_created_at,
            ]
        )

    return output.getvalue()


def generate_payments_csv(data, headers):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)

    for row in data:
        cinetpay_data = row.vn_cinetpay_data.get("data", {})
        writer.writerow(
            [
                row.vn_transaction_id,
                cinetpay_data.get("operator_id", ""),
                row.tenant.vn_fullname,
                row.vn_pay_amount,
                cinetpay_data.get("payment_method", ""),
                cinetpay_data.get("payment_date", ""),
            ]
        )

    return output.getvalue()

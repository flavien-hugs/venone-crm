
import time
import csv
import io
import requests
from flask import Response

def generate_tenant_csv(data, headers):

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)

    for row in data:
        writer.writerow([
            row.vn_tenant_id,
            row.vn_fullname,
            row.vn_phonenumber_one,
            row.vn_addr_email,
            row.vn_cni_number,
            row.vn_profession,
            row.house_tenant.vn_house_rent,
            row.vn_created_at,
        ])

    return output.getvalue()


def generate_owner_csv(data, headers):

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)

    for row in data:
        writer.writerow([
            row.vn_owner_id,
            row.vn_fullname,
            row.vn_phonenumber_one,
            row.vn_addr_email,
            row.vn_cni_number,
            row.vn_profession,
            row.houses.count(),
            row.vn_created_at,
        ])

    return output.getvalue()

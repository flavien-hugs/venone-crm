CIV = "CI - Côte d'Ivoire"
SEN = "SN - Sénégal"
TOG = "TG - Togo"
BF = "BF - Burkina Faso"
CMR = "CM - Cameroun"
RDC = "CG - Congo (Brazzaville)"
GUI = "GN - Guinée"
CON = "CD - Congo (Kinshasa)"
NIG = "NE - Niger"
BEN = "BN - Benin"
MAL = "ML - Mali"
COM = "KM - Comores"

COUNTRY = (
    (CIV, "CI - Côte d'Ivoire"),
    (SEN, "SN - Sénégal"),
    (TOG, "TG - Togo"),
    (BF, "BF - Burkina Faso"),
    (CMR, "CM - Cameroun"),
    (RDC, "CG - Congo (Brazzaville)"),
    (GUI, "GN - Guinée"),
    (CON, "CD - Congo (Kinshasa)"),
    (NIG, "NE - Niger"),
    (BEN, "BN - Benin"),
    (MAL, "ML - Mali"),
    (COM, "KM - Comores"),
)


XOF = "XOF - CFA Franc BCEAO"

DEVICE = (
    (XOF, "XOF - CFA Franc BCEAO"),
)

COUNTRY_DEFAULT = CIV

IS_HOUSE_OWNER = 4
IS_AGENCIE_COMPANY = 6

ACCOUNT_TYPES = (
    (IS_AGENCIE_COMPANY, "Agence Immobilière"),
    (IS_HOUSE_OWNER, "Propriétaire de maison"),
)

ACCOUNT_TYPES_DEFAULT = IS_HOUSE_OWNER


HOMME = "Mr"
FEMME = "Mme"
MDLLE = "Mlle"

GENDER = (
    (HOMME, "Mr"),
    (FEMME, "Mme"),
    (MDLLE, "Mlle"),
)

GENDER_DEFAULT = HOMME

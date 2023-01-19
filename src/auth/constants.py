CIV = "Côte d'Ivoire"
SEN = "Sénégal"
TOG = "Togo"
BF = "Burkina Faso"
CMR = "Cameroun"
RDC = "Congo RDC CDF"
GUI = "Guinée"
CON = "Congo RDC USD"
NIG = "Niger"
BEN = "Benin"
MAL = "Mali"
COM = "Comores"

COUNTRY = (
    (CIV, "Côte d'Ivoire"),
    (SEN, "Sénégal"),
    (TOG, "Togo"),
    (BF, "Burkina Faso"),
    (CMR, "Cameroun"),
    (RDC, "Congo RDC CDF"),
    (GUI, "Guinée"),
    (CON, "Congo RDC USD"),
    (NIG, "Niger"),
    (BEN, "Benin"),
    (MAL, "Mali"),
    (COM, "Comores"),
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

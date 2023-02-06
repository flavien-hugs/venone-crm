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

DEVICE = ((XOF, "XOF - CFA Franc BCEAO"),)

COUNTRY_DEFAULT = CIV


HOMME = "M."
FEMME = "Mme"
MDLLE = "Mlle"

GENDER = (
    (HOMME, "M."),
    (FEMME, "Mme"),
    (MDLLE, "Mlle"),
)

GENDER_DEFAULT = HOMME

STUDIO = "Studio"
VILLA = "Villa"
MAGASIN = "Magasin"

HOUSE_TYPES = ((STUDIO, "Studio"), (VILLA, "Villa"), (MAGASIN, "Magasin"))

DEFAULT_HOUSE_TYPES = VILLA

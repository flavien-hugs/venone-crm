import enum

class Gender(enum.Enum):
    HOMME = "Mr"
    FEMME = "Mme"
    MDLLE = "Mlle"


class Country(enum.Enum):
    CIV = "Côte d'Ivoire"
    BEN = "Benin"
    BF = "Burkina Faso"
    CMR = "Cameroun"
    COM = "Comores"
    RDC = "Congo RDC CDF"
    CON = "Congo RDC USD"
    GUI = "Guinée"
    MAL = "Mali"
    NIG = "Niger"
    SEN = "Sénégal"
    TOG = "Togo"


class AccountType(enum.Enum):
    IS_HOUSE_OWNER = "Propriétaire de maison"
    IS_AGENCIE_COMPANY = "Agence immobilière"

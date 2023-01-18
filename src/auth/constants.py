import enum

class Gender(str, enum.Enum):
    HOMME = "Mr"
    FEMME = "Mme"
    MDLLE = "Mlle"


class Country(str, enum.Enum):
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


class AccountType(str, enum.Enum):
    IS_HOUSE_OWNER = "Propriétaire de maison"
    IS_AGENCIE_COMPANY = "Agence immobilière"

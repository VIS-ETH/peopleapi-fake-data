from dataclasses import dataclass
from typing import Literal

import json


@dataclass
class Programme:
    fvid: str
    fv_name: str
    fachid: str
    programme_name: str
    category: Literal["a", "b", "c", "d", "e", "f", "g"]
    dept: str


BANKS = (
    "Nidwaldner Kantonalbank",
    "Zürcher Kantonalbank",
    "CS",
    "UBS",
    "PostFinance",
    "Bündner Kantonalbank",
    "Raiffeisen",
    "Vontobel",
    "Banque Cantonale de Genève",
    "Basler Kantonalbank",
)

type MembershipType = Literal[
    "VSETH_MEMBERSHIP_TYPE_UNSPECIFIED",  #
    "VSETH_MEMBERSHIP_TYPE_BACHELOR_OR_MASTER",  # a
    "VSETH_MEMBERSHIP_TYPE_PHD",  # b
    "VSETH_MEMBERSHIP_TYPE_VSETH_EMPLOYEES",  # c
    "VSETH_MEMBERSHIP_TYPE_ETH_APPRENTICES",  # d
    "VSETH_MEMBERSHIP_TYPE_MOBILITY_STUDENTS",  # e
    "VSETH_MEMBERSHIP_TYPE_STUDENTS_IN_CONTINUING_EDUCATION",  # f
    "VSETH_MEMBERSHIP_TYPE_AUDITORS",  # g
]

membershipMap: dict[Literal["a", "b", "c", "d", "e", "f", "g"], MembershipType] = {
    "a": "VSETH_MEMBERSHIP_TYPE_BACHELOR_OR_MASTER",  # a
    "b": "VSETH_MEMBERSHIP_TYPE_PHD",  # b
    "c": "VSETH_MEMBERSHIP_TYPE_VSETH_EMPLOYEES",  # c
    "d": "VSETH_MEMBERSHIP_TYPE_ETH_APPRENTICES",  # d
    "e": "VSETH_MEMBERSHIP_TYPE_MOBILITY_STUDENTS",  # e
    "f": "VSETH_MEMBERSHIP_TYPE_STUDENTS_IN_CONTINUING_EDUCATION",  # f
    "g": "VSETH_MEMBERSHIP_TYPE_AUDITORS",  # g
}


KOMMISSION_DOMAINS = (
    "challenge.swiss",
    "vseth.ethz.ch",
    "ethmun.org",
    "exbeerience.ethz.ch",
    "filmstelle.ch",
    "polymesse.ch",
    "flik.ethz.ch",
    "geco.ethz.ch",
    "vseth.ethz.ch",
    "kulturstelle.ch",
    "nightline.ch",
    "polykum.ethz.ch",
    "papperlapub.ethz.ch",
    "ssc.ethz.ch",
    "tanzquotient.org",
    "fotokommssion.ch",
    "vseth.ethz.ch",
    "thealternative.ch",
    "winafe.ch",
    "vseth.ethz.ch",
)

DEPARTMENTS = (
    "D-ARCH",
    "D-BAUG",
    "D-BIOL",
    "D-BSSE",
    "D-CHAB",
    "D-EAPS",
    "D-GESS",
    "D-HEST",
    "D-INFK",
    "D-ITET",
    "D-MATH",
    "D-MATL",
    "D-MAVT",
    "D-MTEC",
    "D-PHYS",
    "D-USYS",
)


@dataclass
class StudyInfo:  # take random pick from zuordnungsliste, to get fv and dept
    ethFachid: str
    department: str
    departmentDisplayLabelDe: str
    departmentDisplayLabelEn: str
    studyProgramDisplayLabelDe: str
    studyProgramDisplayLabelEn: str
    studyFachrichtungDisplayLabelDe: str
    studyFachrichtungDisplayLabelEn: str
    exitDate: str


@dataclass
class VsethMemberInfo:
    membership: Literal[
        "VSETH_MEMBERSHIP_UNSPECIFIED",
        "VSETH_MEMBERSHIP_MEMBER",
        "VSETH_MEMBERSHIP_NOT_MEMBER",
    ]
    membershipType: MembershipType
    fvOrgId: str
    fvOrgKey: str


@dataclass
class VsethPostAddr:
    streetAddress: str
    locality: str  # Zürich
    postalCode: str  # 1234
    country: str  # CH


type BankAddress = VsethPostAddr  # equivalent for now


@dataclass
class VsethBank:
    bankName: str
    bic: str
    iban: str
    accountHolderName: str  # might be different from person name
    bankingAddress: BankAddress


EMPTY_BANK = VsethBank(
    accountHolderName="",
    bankingAddress=VsethPostAddr("", "", "", ""),
    bankName="",
    bic="",
    iban="",
)


@dataclass
class FakeUser:
    username: str
    password: str
    firstName: str
    lastName: str
    mail: str
    telephoneNumber: str
    vsethPersonId: str
    vsethStudentNumber: str
    vsethAlternativeEmail: str
    vsethStudySemester: int
    vsethBirthDate: str
    vsethCreateTime: str
    vsethUpdateTime: str
    vsethEthStudyInfo: StudyInfo
    vsethMembershipInfo: VsethMemberInfo
    vsethPostalAddress: VsethPostAddr
    vsethBankAccount: VsethBank
    vsethSwissEduPersonUniqueId: str  # number @ institution
    vsethSwissEduPersonAffiliation: str
    vsethAdvantUid: str
    vsethKabaGroupHeader: str

    def toJSON(self):
        return json.dumps(
            self, ensure_ascii=False, default=lambda o: o.__dict__, indent=4
        )

    def toJSONL(self):
        return json.dumps(
            self,
            ensure_ascii=False,
            separators=(",", ":"),
            default=lambda o: o.__dict__,
        )


FUNNY_ADDRESSES: list[VsethPostAddr] = [
    VsethPostAddr(
        country="United Kingdom",
        locality="Middlesbrough",
        postalCode="TS42HT",
        streetAddress="0 Egmont Road",
    ),
    VsethPostAddr(
        country="USA",
        locality="Boston",
        postalCode="MA 02109",
        streetAddress="Ten Post office Sq",
    ),
]

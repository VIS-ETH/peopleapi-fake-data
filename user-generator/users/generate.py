from enum import Enum, auto
from random import Random
from typing import Optional
import logging
import faker
from users.models import (
    BANKS,
    DEPARTMENTS,
    EMPTY_BANK,
    EMPTY_STUDY_INFO,
    FUNNY_ADDRESSES,
    FV_GROUPS,
    FV_MEMBER_EXTRA_GROUPS,
    KOMMISSION_DOMAINS,
    FakeUser,
    Programme,
    StudyInfo,
    VsethBank,
    VsethMemberInfo,
    VsethPostAddr,
    membershipMap,
)
from users.programmes import programmes


OUTPUT_JSONL = False

IS_ACTIVE_PROB = 0.4
FULLNAME_EMAIL_PROB = 0.1
IS_VSETH_MEMBER_PROB = 0.8
BANK_ACCOUNT_IS_OWN_NAME = 0.9
HAS_BANK_INFO = 0.6
IS_STUDENT_AND_STAFF = 0.2
DO_FUNNY_ADDR = 0.1
UZH_SHARE = 0.1
UZH_IS_STAFF = 0.1
UZH_IS_VIS_EXTRA = 0.4
OTHER_FV_IS_VIS_EXTRA = 0.1
VIS_ORG_ID = "1116"
VIS_EXTRA_GROUPS = ("vseth-1602-fvextra-vis", "vseth-1116-vis")


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.236+0100"


class MailDomains(Enum):
    FV = auto()
    KOM = auto()
    VSETH = auto()


MAIL_DOMAIN_AND_WEIGHT = (
    (MailDomains.FV, 0.6),
    (MailDomains.KOM, 0.1),
    (MailDomains.VSETH, 0.3),
)


class UserFaker:
    usernames: set[str]
    advant_uids: set[str]
    prestigeEmails: set[str]
    uzh_mails: set[str]
    all_faker: faker.Faker
    swiss_faker: faker.Faker
    random: Random
    seed: Optional[int] = None
    uzh_share: float
    mail_population: tuple[MailDomains, ...]
    mail_weights: tuple[float, ...]

    def __init__(
        self, seed: Optional[int] = None, uzh_share: float = UZH_SHARE
    ) -> None:
        self.usernames = set()
        self.advant_uids = set()
        self.prestigeEmails = set()
        self.uzh_mails = set()
        self.uzh_share = uzh_share
        self.swiss_faker = faker.Faker(locale=["de_CH"])
        self.all_faker = faker.Faker()
        self.random = Random()
        if seed is not None:
            self.random.seed(a=seed)
            faker.Faker.seed(seed)

        self.mail_population = tuple(t[0] for t in MAIL_DOMAIN_AND_WEIGHT)
        self.mail_weights = tuple(t[1] for t in MAIL_DOMAIN_AND_WEIGHT)

    def generate_many(self, n=1) -> list[FakeUser]:
        res: list[FakeUser] = []
        for _ in range(n):
            res.append(self.generate_user())
        return res

    def generate_username(self, firstname, lastname) -> str:
        # basic f[l...]
        uname = firstname[:1] + lastname
        if uname not in self.usernames:
            self.usernames.add(uname)
            return uname
        # ff[l...]
        if len(firstname) > 1:
            uname = firstname[:2] + lastname
            if uname not in self.usernames:
                self.usernames.add(uname)
                return uname
        # [l...]f
        uname = lastname + firstname[:1]
        if uname not in self.usernames:
            self.usernames.add(uname)
            return uname
        uname = lastname[:-1] + firstname[:1]
        if uname not in self.usernames:
            self.usernames.add(uname)

        # last resort
        uname = firstname[:1] + lastname
        i = 1
        while uname + (str(i).zfill(2)) in self.usernames:
            i += 1
        uname = uname + (str(i).zfill(2))
        self.usernames.add(uname)

        return uname

    def pick_programme(self):
        selection = self.random.choice(programmes)
        # print(selection)
        fvid, fv_name, fachid, programme, category = selection
        dept = self.random.choice(DEPARTMENTS)
        return Programme(fvid, fv_name, fachid, programme, category, dept)

    def get_alt_email(self, first, last, username, fv: str) -> str:
        # returns an "alternative email", doesn't neccessarily have to end with fv,
        # since could also be kommission or vseth
        is_active = self.random.random() <= IS_ACTIVE_PROB
        email_suffix = self.random.choices(
            population=self.mail_population,
            weights=self.mail_weights,
            k=1,
        )[0]
        has_fullname_email = self.random.random() <= FULLNAME_EMAIL_PROB
        komm_domain = self.random.choice(KOMMISSION_DOMAINS)

        if not is_active:
            return ""

        prefix = username
        if has_fullname_email:
            prefix = f"{first}.{last}"

        suffix_map = {
            MailDomains.FV: f"{fv}.ethz.ch",
            MailDomains.KOM: komm_domain,
            MailDomains.VSETH: "vseth.ethz.ch",
        }

        mail = f"{prefix}@{suffix_map[email_suffix]}"
        if has_fullname_email and mail in self.prestigeEmails:
            logging.warning("got prestigeAlias conflict")
            prefix = f"{last}.{first}"
            mail = f"{prefix}@{suffix_map[email_suffix]}"
            if mail in self.prestigeEmails:
                logging.warning("got 2 levels of conflict!!")
                prefix = f"{first}.{last}1"
                mail = f"{prefix}@{suffix_map[email_suffix]}"
                if mail in self.prestigeEmails:
                    logging.warning("got 3 levels of conflict!!")
                    prefix = f"{last}.{first}1"
                    mail = f"{prefix}@{suffix_map[email_suffix]}"
                    if mail in self.prestigeEmails:
                        logging.error("Too many conflicts!")
                        exit(1)
        if has_fullname_email:
            self.prestigeEmails.add(mail)
        return mail

    def generate_email(self, username: str) -> str:
        # TODO more variety
        return f"{username}@student.ethz.ch"

    def generate_study_info(self, programme_pick: Programme) -> StudyInfo:
        return StudyInfo(
            ethFachid=programme_pick.fachid,
            department=programme_pick.dept,
            departmentDisplayLabelDe="TODO",
            departmentDisplayLabelEn="TODO",
            studyFachrichtungDisplayLabelDe=programme_pick.programme_name,
            studyFachrichtungDisplayLabelEn=programme_pick.programme_name,
            studyProgramDisplayLabelDe=programme_pick.programme_name,
            studyProgramDisplayLabelEn=programme_pick.programme_name,
            exitDate=self.all_faker.future_date(end_date="+2y").strftime(DATE_FORMAT),
        )

    def generate_vseth_info(self, programme: Programme) -> VsethMemberInfo:
        is_vseth_member = self.random.random() <= IS_VSETH_MEMBER_PROB

        if not is_vseth_member:
            return VsethMemberInfo(
                membership="VSETH_MEMBERSHIP_NOT_MEMBER",
                membershipType="VSETH_MEMBERSHIP_TYPE_UNSPECIFIED",
                fvOrgId="",
                fvOrgKey="",
            )

        return VsethMemberInfo(
            membership="VSETH_MEMBERSHIP_MEMBER",
            membershipType=membershipMap[programme.category],
            fvOrgId=programme.fvid,
            fvOrgKey=programme.fv_name,
        )

    def generate_address(self) -> VsethPostAddr:
        """Generate a (mostly) swiss looking address
        if you ever seriously want to process addresses, keep this in mind:
        https://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/"""
        potential_funny = self.random.choice(FUNNY_ADDRESSES)
        if self.random.random() <= DO_FUNNY_ADDR:
            return potential_funny
        return VsethPostAddr(
            streetAddress=self.swiss_faker.street_address(),
            locality=self.swiss_faker.city(),
            postalCode=self.swiss_faker.postcode(),
            country="CH",
        )

    def generate_bank_info(self, first: str, last: str) -> VsethBank:
        """Generate swiss looking bank info
        BIC/Swift will not match the Bank name
        (or any bank for that matter), but is well-formed swiss Swift code
        """
        is_own_bank_acc = self.random.random() <= BANK_ACCOUNT_IS_OWN_NAME
        if not is_own_bank_acc:
            first = self.all_faker.first_name()
            last = self.all_faker.last_name()

        bank_name = self.random.choice(BANKS)
        bic = self.swiss_faker.swift(
            length=11
        )  # bic and swift are the same, faker.bic is some russian bank thingy(??)
        iban = self.swiss_faker.iban()
        account_holder = f"{first} {last}"
        bank_addr = self.generate_address()

        return VsethBank(
            accountHolderName=account_holder,
            bankingAddress=bank_addr,
            bankName=bank_name,
            bic=bic,
            iban=iban,
        )

    def generate_advant_uid(self) -> str:
        uid = self.all_faker.hexify("^^^^^^^^^^^^^^", upper=True)
        while uid in self.advant_uids:
            uid = self.all_faker.hexify("^^^^^^^^^^^^^^", upper=True)
        self.advant_uids.add(uid)
        return uid

    def generate_groups(self, membership_info: VsethMemberInfo) -> list[str]:
        """VSETH members are in the group of their Fachverein.
        Some members of other Fachvereine are extraordinary members of VIS."""
        if membership_info.membership != "VSETH_MEMBERSHIP_MEMBER":
            return []
        fv_group = FV_GROUPS.get(membership_info.fvOrgId)
        if fv_group is None:  # e.g. 0200 (VSETH itself), no FV
            return []
        groups = [*FV_MEMBER_EXTRA_GROUPS.get(membership_info.fvOrgId, ()), fv_group]
        if (
            membership_info.fvOrgId != VIS_ORG_ID
            and self.random.random() <= OTHER_FV_IS_VIS_EXTRA
        ):
            groups += VIS_EXTRA_GROUPS
        return groups

    def generate_uzh_groups(self) -> list[str]:
        """Some UZH people are extraordinary members of VIS"""
        if self.random.random() <= UZH_IS_VIS_EXTRA:
            return list(VIS_EXTRA_GROUPS)
        return []

    def generate_uzh_email(self, first: str, last: str) -> str:
        """UZH addresses look like firstname.lastname@uzh.ch"""
        prefix = f"{first}.{last}".replace(" ", "")
        mail = f"{prefix}@uzh.ch"
        i = 1
        while mail in self.uzh_mails:
            i += 1
            mail = f"{prefix}{i}@uzh.ch"
        self.uzh_mails.add(mail)
        return mail

    def generate_common(self) -> dict:
        """Fields every person has, regardless of institution"""
        first = self.all_faker.first_name()
        last = self.all_faker.last_name()
        create_datetime_raw = self.all_faker.past_datetime(start_date="-20y")
        update_datetime = self.all_faker.past_datetime(
            start_date=create_datetime_raw
        ).strftime(DATETIME_FORMAT)

        bank_info = self.generate_bank_info(first, last)
        if self.random.random() > HAS_BANK_INFO:
            bank_info = EMPTY_BANK

        return dict(
            username=self.generate_username(first.lower(), last.lower()),
            password=self.all_faker.password(length=8),
            firstName=first,
            lastName=last,
            telephoneNumber=self.swiss_faker.phone_number(),
            vsethPersonId=self.all_faker.hexify(
                "^^^^^^^^-^^^^-^^^^-^^^^-^^^^^^^^^^^^"
            ),
            vsethBirthDate=self.all_faker.date_of_birth(
                minimum_age=14, maximum_age=101
            ).strftime(DATE_FORMAT),
            vsethCreateTime=create_datetime_raw.strftime(DATETIME_FORMAT),
            vsethUpdateTime=update_datetime,
            vsethPostalAddress=self.generate_address(),
            vsethBankAccount=bank_info,
        )

    def generate_user(self) -> FakeUser:
        if self.random.random() < self.uzh_share:
            return self.generate_uzh_user()
        return self.generate_eth_user()

    def generate_uzh_user(self) -> FakeUser:
        """External person studying at UZH: no ETH study info, no VSETH
        membership and no Legi (advant/kaba). Some are extraordinary VIS members"""
        common = self.generate_common()
        start_year = self.all_faker.past_date(start_date="-12y").year
        affil = "member;student"
        if self.random.random() <= UZH_IS_STAFF:
            affil += ";staff"

        return FakeUser(
            **common,
            mail=self.generate_uzh_email(
                common["firstName"].lower(), common["lastName"].lower()
            ),
            vsethStudentNumber=self.all_faker.numerify(
                f"{str(start_year)[-2:]}######"
            ),
            vsethAlternativeEmail="",
            vsethStudySemester=self.random.randint(1, 14),
            vsethEthStudyInfo=EMPTY_STUDY_INFO,
            vsethMembershipInfo=VsethMemberInfo(
                membership="VSETH_MEMBERSHIP_NOT_MEMBER",
                membershipType="VSETH_MEMBERSHIP_TYPE_UNSPECIFIED",
                fvOrgId="",
                fvOrgKey="",
            ),
            vsethSwissEduPersonUniqueId=self.all_faker.numerify("#######")
            + "@uzh.ch",
            vsethSwissEduPersonAffiliation=affil,
            vsethAdvantUid="",
            vsethKabaGroupHeader="",
            groups=self.generate_uzh_groups(),
        )

    def generate_eth_user(self) -> FakeUser:
        programme_pick = self.pick_programme()
        common = self.generate_common()
        username = common["username"]

        start_year_two_digit = str(self.all_faker.past_date(start_date="-80y").year)[
            :-2
        ]
        student_number = self.all_faker.numerify(f"{start_year_two_digit}######")
        alt_email = self.get_alt_email(
            common["firstName"].lower(),
            common["lastName"].lower(),
            username,
            programme_pick.fv_name,
        )

        membership_info = self.generate_vseth_info(programme_pick)

        edu_person_affil = "member;student"
        if self.random.random() <= IS_STUDENT_AND_STAFF:
            edu_person_affil += ";staff"

        return FakeUser(
            **common,
            mail=self.generate_email(username),
            vsethStudentNumber=student_number,
            vsethAlternativeEmail=alt_email,
            vsethStudySemester=self.random.randint(1, 20),
            vsethEthStudyInfo=self.generate_study_info(programme_pick),
            vsethMembershipInfo=membership_info,
            vsethSwissEduPersonUniqueId=self.all_faker.numerify("#######")
            + "@ethz.ch",
            vsethSwissEduPersonAffiliation=edu_person_affil,
            vsethAdvantUid=self.generate_advant_uid(),
            vsethKabaGroupHeader=self.all_faker.numerify("%#####"),
            groups=self.generate_groups(membership_info),
        )


def main():
    user_faker = UserFaker(seed=2)
    u = user_faker.generate_many(50)
    start = True
    print("[")
    for a in u:
        if start:
            start = False
        else:
            print(",")
        print(a.toJSON(), end="")
    print("]")


if __name__ == "__main__":
    main()

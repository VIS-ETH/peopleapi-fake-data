from enum import Enum, auto
from random import Random
from typing import Optional
import logging
import faker
from users.models import (
    BANKS,
    DEPARTMENTS,
    EMPTY_BANK,
    FUNNY_ADDRESSES,
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


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f+0100"


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
    all_faker: faker.Faker
    swiss_faker: faker.Faker
    random: Random
    seed: Optional[int] = None
    mail_population: tuple[MailDomains, ...]
    mail_weights: tuple[float, ...]

    def __init__(self, seed: Optional[int] = None) -> None:
        self.usernames = set()
        self.advant_uids = set()
        self.prestigeEmails = set()
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

    def generate_user(self):

        programme_pick = self.pick_programme()

        pw = self.all_faker.password(length=8)
        first = self.all_faker.first_name()
        last = self.all_faker.last_name()
        username = self.generate_username(first.lower(), last.lower())
        mail = self.generate_email(username)
        phone = self.swiss_faker.phone_number()

        person_id = self.all_faker.hexify("^^^^^^^^-^^^^-^^^^-^^^^-^^^^^^^^^^^^")
        start_year_two_digit = str(self.all_faker.past_date(start_date="-80y").year)[
            :-2
        ]
        student_number = self.all_faker.numerify(f"{start_year_two_digit}######")
        alt_email = self.get_alt_email(
            first.lower(),
            last.lower(),
            username,
            programme_pick.fv_name,
        )
        study_semester = self.random.randint(1, 20)

        birthdate = self.all_faker.date_of_birth(
            minimum_age=14, maximum_age=101
        ).strftime(DATE_FORMAT)
        create_datetime_raw = self.all_faker.past_datetime(start_date="-20y")
        update_datetime = self.all_faker.past_datetime(
            start_date=create_datetime_raw
        ).strftime(DATETIME_FORMAT)
        create_datetime = create_datetime_raw.strftime(DATETIME_FORMAT)

        eth_study_info: StudyInfo = self.generate_study_info(programme_pick)

        membership_info: VsethMemberInfo = self.generate_vseth_info(programme_pick)

        # if (
        #     membership_info.membership != "VSETH_MEMBERSHIP_MEMBER"
        # ):  # can't be vseth member without being vseth member, right?
        #     alt_email = ""

        vseth_postal = self.generate_address()

        bank_info = self.generate_bank_info(first, last)
        has_bank_info = self.random.random() <= HAS_BANK_INFO
        if not has_bank_info:
            bank_info = EMPTY_BANK

        edu_person_unique = self.all_faker.numerify("#######") + "@ethz.ch"
        edu_person_affil = "member;student"
        if self.random.random() <= IS_STUDENT_AND_STAFF:
            edu_person_affil += ";staff"

        # print(
        #     username.center(20), alt_email.ljust(30), first, last, programme_pick.dept
        # )
        advant_uid = self.generate_advant_uid()
        kaba_group_header = self.all_faker.numerify("%#####")
        user = FakeUser(
            username=username,
            password=pw,
            firstName=first,
            lastName=last,
            mail=mail,
            telephoneNumber=phone,
            vsethPersonId=person_id,
            vsethStudentNumber=student_number,
            vsethAlternativeEmail=alt_email,
            vsethStudySemester=study_semester,
            vsethBirthDate=birthdate,
            vsethCreateTime=create_datetime,
            vsethUpdateTime=update_datetime,
            vsethEthStudyInfo=eth_study_info,
            vsethMembershipInfo=membership_info,
            vsethPostalAddress=vseth_postal,
            vsethBankAccount=bank_info,
            vsethSwissEduPersonUniqueId=edu_person_unique,
            vsethSwissEduPersonAffiliation=edu_person_affil,
            vsethAdvantUid=advant_uid,
            vsethKabaGroupHeader=kaba_group_header,
        )
        return user


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

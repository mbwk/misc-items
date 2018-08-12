#!/usr/bin/env python3

# direct.py - a script for verifying save files

import itertools
from datetime import datetime
import xml.etree.ElementTree as ET
from hashlib import sha1

def sha1sum(inputstring):
    if type(inputstring) == str:
        inputstring = inputstring.encode()
    return sha1(inputstring).hexdigest().upper()
    
DEOBFUSCATION = (
    ("IIIlIlIlIIllIIlllllIllllIlIlllll", "first-section"),
    ("IllIIlIllIlIlIIlIIlIIIlIllIIllll", "first-key"),
    ("IIIIIIlIIIIlll", "second-section"),
    ("lIlllIllIIlIlI", "second-key"),
    ("K2YRUK77", "unknown-section"),
    ("AKSS3SE0", "unknown-key"),
    ("IIlIlIIlllIIII", "points-section"),
    ("IllIIIIIlIIIII", "points-key"),
    ("lllIlIlIllIllI", "units-section"),
    ("IlIIllIIllllll", "units-key-killed"),
    ("IlllllllIlIllI", "units-key-lost"),
    ("lIlIIlIllllIllIl", ""),
    ("IIllllIIIlllIIlI", ""),
    ("lIlIlllIlIIIlIIllllIllllIlllIIll", ""),
    ("IIIlIlIlllIIIIllIlIIllIlllIIlIIl", ""),
)

class BankInfo():
    def __init__(self, title):
        self.title = title

class SectionKey():
    def __init__(self, name, keyType, value):
        self.name = name
        self.type = keyType
        self.value = value

    def __repr__(self):
        return "SectionKey(name={}, type={}, value={})".format(
            repr(self.name),
            repr(self.type),
            repr(self.value),
        )

class Section():
    def __init__(self, name, keys=None):
        self.name = name
        self.keys = keys if keys else list()

    def __repr__(self):
        return "Section(name={}, keys={})".format(
            repr(self.name),
            repr(self.keys),
        )

class BankInfo():
    def __init__(self, name, player_number, author_number):
        self.name = name
        self.player_number = player_number
        self.author_number = author_number

    def __repr__(self):
        return "BankInfo(name={}, player_number={}, author_number={})".format(
            repr(self.name),
            repr(self.player_number),
            repr(self.author_number),
        )

class Bank():
    def __init__(self, bank_info, version, sections=None, signature=None):
        self.bank_info = bank_info
        self.version = version
        self.sections = sections if sections else list()
        self.signature = signature if signature else ""

    def __repr__(self):
        return "Bank(bank_info={}, version={}, sections={}, signature={})".format(
            repr(self.bank_info),
            repr(self.version),
            repr(self.sections),
            repr(self.signature),
        )

    def signature_inputstring(self) -> str:
        input_items = [
            self.bank_info.author_number,
            self.bank_info.player_number,
            self.bank_info.name,
        ]
        def strord(c):
            return sum([ord(i) for i in c], 0)
        def ordsort(iterable):
            return sorted(iterable, key=lambda a: strord(a.name))
        def lexsort(iterable):
            return sorted(iterable, key=lambda a: a.name)
        sortfun = lexsort
        for s in sortfun(self.sections):
            input_items.append(s.name)
            for k in sortfun(s.keys):
                input_items.extend([
                    k.name,
                    "Value",
                    k.type,
                    k.value,
                ])
        return "".join(input_items)

    def generate_signature(self) -> str:
        return sha1sum(self.signature_inputstring())

    def verify_signature(self) -> bool:
        return self.signature == self.generate_signature()

    def to_file(self, filepath):
        raise NotImplementedError

def bank_from_file(filepath, player, author) -> Bank:
    e = ET.parse(filepath).getroot()
    sections = [
        Section(name=s.attrib["name"], keys=[
            SectionKey(k.attrib["name"],
                list(v.attrib.keys())[0],
                list(v.attrib.values())[0])
            for k, v in [ (fk, fk.find("Value")) for fk in s.findall("Key") ]
        ]) for s in e.findall("Section")
    ]

    filename = filepath.rpartition("/")[-1].partition(".")[0]
    new_bank = Bank(BankInfo(
        filename,
        player,
        author,
    ), "1", sections, e.find("Signature").attrib["value"])
    return new_bank

def load_save_file(filepath) -> dict:
    savedata = dict()


def main(filepath, player, author):
    b = bank_from_file(filepath, player, author)
    print("Bank data:")
    print(b)
    print()
    print("Input String:")
    print(b.signature_inputstring())
    print()
    print("Present signature:")
    print(b.signature)
    print()
    print("Algorithm generated signature:")
    print(b.generate_signature())
    print()
    print("Match? {}".format(b.verify_signature()))

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])


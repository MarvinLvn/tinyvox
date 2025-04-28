import pytest
from chat_toolkit.cleaner import ChatCleaner

@pytest.fixture
def cleaner():
    return ChatCleaner()

def test_fragments(cleaner):
    assert cleaner.clean("m(u)mmy") == "mummy"
    assert cleaner.clean("nothin(g)") == "nothing"
    assert cleaner.clean("I'm (a)bout to put some algae eaters in there") == "I'm about to put some algae eaters in there"
    assert cleaner.clean("y(ou) all wanna go play together") == "you all wanna go play together"
    assert cleaner.clean("b(r)aco je ulovio (r)ibicu") == "braco je ulovio ribicu"
    assert cleaner.clean("(l)opaticom") == "lopaticom"
    assert cleaner.clean("a(j)hajmo") == "ajhajmo"

def test_unintelligible_speech(cleaner):
    assert cleaner.clean("did you get xxx xxx ?") == "did you get xxx xxx ?"
    assert cleaner.clean("I saw xxx playing") == "I saw xxx playing"
    assert cleaner.clean("xxx xxx xxx") == "xxx xxx xxx"

def test_fillers(cleaner):
    assert cleaner.clean("&-um grapes .") == "grapes ."
    assert cleaner.clean("stupid &+ss .") == "stupid ."
    assert cleaner.clean("and I also like &+cla Aquarium_Adventures .") == "and I also like aquarium adventures ."

def test_special_markers(cleaner):
    assert cleaner.clean("I wanna ↫pl↫play .") == "I wanna play ."
    assert cleaner.clean("sonra iste tepenin ustune cikiyo .15480_17440") == "sonra iste tepenin ustune cikiyo"


def test_scoped_annotations(cleaner):
    assert cleaner.clean("<dan str(ooit)> [//] dan giet ze het water over de bloemen .") == "dan strooit dan giet ze het water over de bloemen ."
    assert cleaner.clean("&~ehm de ridder die [/] die was net komen kijken .") == "de ridder die die was net komen kijken ."


def test_trailing_off(cleaner):
    # Basic trailing off
    assert cleaner.clean(
        "I have (.) three cats that I I have to take +…") == "I have three cats that I I have to take ..."

    # ASCII dots version
    assert cleaner.clean("we use algae fly +...") == "we use algae fly ..."

    # Mixed with other markers
    assert cleaner.clean("+, we use algae fly +…") == "we use algae fly ..."
    assert cleaner.clean("he &+sta +…") == "he ..."

    # Make sure we don't over-replace
    assert cleaner.clean("this is... a test") == "this is... a test"

def test_replacements(cleaner):
    # Keep original forms
    assert cleaner.clean("gonna [: going to] go gonna [: going to] go") == "gonna go gonna go"
    assert cleaner.clean("+< podo [: posso] podo [: posso] .") == "podo podo ."

    # Other examples from the list
    assert cleaner.clean("whyncha [: why don't you] just be quiet!") == "whyncha just be quiet!"
    assert cleaner.clean("der futtog@o bil .") == "der futtog bil ."
    assert cleaner.clean("a@p kører futtog@o .") == "a kører futtog ."

    # Complex cases with other annotations
    assert cleaner.clean(
        "<because I think it's> [/] because I think it's gonna [: going to] rain") == "because I think it's because I think it's gonna rain"

def test_pauses(cleaner):
    assert cleaner.clean("I have (.) three cats that I I have to take +…") == "I have three cats that I I have to take ..."

def test_complex_cases(cleaner):
    assert cleaner.clean("<Jea est-c(e) que tu peux laisser ça et aller t(e) mett(re) en pyjama> [= ! baille] .") == "Jea est-ce que tu peux laisser ça et aller te mettre en pyjama ."
    assert cleaner.clean("der futtog@o bil .") == "der futtog bil ."
    assert cleaner.clean("a@p kører futtog@o .") == "a kører futtog ."

def test_underscore_terms(cleaner):
    assert cleaner.clean("they probably have Sour_Patch_Kids in them .") == "they probably have sour patch kids in them ."
    assert cleaner.clean("going to Toy_R_Us today") == "going to toy r us today"
    assert cleaner.clean("watching Power_Rangers_Show now") == "watching power rangers show now"

def test_trailing_off_question(cleaner):
    assert cleaner.clean("so you have one brib +..?") == "so you have one brib ?"
    assert cleaner.clean("what should we +..?") == "what should we ?"
    assert cleaner.clean("where did you +..?") == "where did you ?"


def test_timestamps_from_file(cleaner):
    # Test cases from the actual file
    assert cleaner.clean(
        "sonra domates adam donerek havaya dogru cikiyo .12800_15440") == "sonra domates adam donerek havaya dogru cikiyo"
    assert cleaner.clean("sonra do .13120_13480") == "sonra do"
    assert cleaner.clean("mates adam .13680_14080") == "mates adam"
    assert cleaner.clean("donere .14120_14480") == "donere"
    assert cleaner.clean("cikiyo .15240_15440") == "cikiyo"
    assert cleaner.clean("sonra iste tepenin ustune cikiyo .15480_17440") == "sonra iste tepenin ustune cikiyo"
    assert cleaner.clean("&=NA .15480_15800") == ""  # Note: FillerCleaner will handle &=NA later

    # Additional edge cases
    assert cleaner.clean(".15480_17440") == ""  # only timestamp
    assert cleaner.clean("text .15480_17440 more") == "text more"


def test_timestamps_with_control_chars(cleaner):
    assert cleaner.clean(
        "sonra domates adam donerek havaya dogru cikiyo .^U12800_15440^U") == "sonra domates adam donerek havaya dogru cikiyo"
    assert cleaner.clean("sonra do .^U13120_13480^U") == "sonra do"
    assert cleaner.clean("&=NA .^U15480_15800^U") == ""

    # Also test without control chars to ensure backward compatibility
    assert cleaner.clean("sonra iste tepenin ustune cikiyo .15480_17440") == "sonra iste tepenin ustune cikiyo"


def test_additional_patterns(cleaner):
    # Overlap and uncertainty markers
    assert cleaner.clean("+< sim [?] .") == "sim ."

    # Complex case with fragments and pauses
    assert cleaner.clean("não [?] (.) e ago(r)a (.) ti(r)o (.) (es)tá bem ?") == "não e agora tiro está bem ?"

    # Postcodes
    assert cleaner.clean("this one Mama . [+ SR]") == "this one Mama ."
    assert cleaner.clean("of this xxx look [>] . [+ PI]") == "of this xxx look ."

    # Additional test cases
    assert cleaner.clean("word [?] (.) other (wo)rd") == "word other word"
    assert cleaner.clean("text [>] with postcode [+ XX]") == "text with postcode"
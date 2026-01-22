# ENGLISH PHONEMES - BROADER TRANSCRIPTION
english_consonants = {
    # Plosives/Stops
    'p',  # pen, spin
    'b',  # bad, rub
    't',  # top, star
    'd',  # dog, red
    'k',  # cat, skin
    'ɡ',  # get, big

    # Fricatives
    'f',  # fan, leaf
    'v',  # van, leave
    'θ',  # thin, teeth
    'ð',  # this, breathe
    's',  # sit, face
    'z',  # zoo, days
    'ʃ',  # she, wish
    'ʒ',  # measure, beige
    'h',  # hat, ahead

    # Nasals
    'm',  # man, sum
    'n',  # no, sun
    'ŋ',  # sing, long

    # Approximants
    'l',  # let, fall
    'ɹ',  # red, very (using ɹ instead of r for accuracy)
    'j',  # yes, use
    'w',  # wet, away
}

english_vowels = {
    # Monophthongs
    'i',  # see, heat (can be marked iː)
    'ɪ',  # sit, bin
    'e',  # say (used in some systems instead of eɪ)
    'ɛ',  # get, bed
    'æ',  # cat, bad
    'a',  # broader symbol for open vowels
    'ɑ',  # father, palm
    'ɔ',  # caught, law
    'o',  # go (used in some systems instead of oʊ)
    'ʊ',  # put, good
    'u',  # blue, food (can be marked uː)
    'ʌ',  # cut, but
    'ə',  # about, sofa (unstressed)
    'ɜ',  # bird (non-rhotic, can be marked ɜː)
}

# GERMAN PHONEMES - BROADER TRANSCRIPTION

german_consonants = {
    # Plosives/Stops
    'p',  # Paar, Suppe
    'b',  # Bein, haben
    't',  # Tag, Mitte
    'd',  # Dach, oder
    'k',  # Kanne, Ecke
    'ɡ',  # gut, Tage

    # Fricatives
    'f',  # Fisch, Hafen
    'v',  # Wasser, Löwe
    's',  # Haus, Straße
    'z',  # Sohn, Hase
    'ʃ',  # Schule, waschen
    'ç',  # ich, Licht
    'x',  # Bach, kochen
    'h',  # Haus, sehen

    # Nasals
    'm',  # Mutter, kommen
    'n',  # nein, können
    'ŋ',  # singen, lang

    # Approximants/Liquids
    'l',  # Leben, Stille
    'j',  # ja, Jahr
    'ʁ',  # rot, fahren (uvular)
}

german_vowels = {
    # Short vowels
    'ɪ',  # Bitte, Kind
    'ɛ',  # Bett, Männer
    'œ',  # Hölle, Götter
    'a',  # Mann, Klasse
    'ɔ',  # Koffer, voll
    'ʊ',  # Mutter, Mund
    'ə',  # bitte (final e)

    # Long vowels
    'i',  # Lied, Tier (marked as iː in precise transcription)
    'y',  # früh, führen (marked as yː in precise transcription)
    'e',  # Beet, Weg (marked as eː in precise transcription)
    'ø',  # schön, Öl (marked as øː in precise transcription)
    'a',  # Bahn, Staat (marked as aː in precise transcription)
    'o',  # Boot, Ofen (marked as oː in precise transcription)
    'u',  # Buch, Schule (marked as uː in precise transcription)
}

# FRENCH PHONEMES - BROADER TRANSCRIPTION

french_consonants = {
    # Plosives/Stops
    'p',  # pain, père
    'b',  # bon, belle
    't',  # tu, tête
    'd',  # dans, dire
    'k',  # que, qui
    'ɡ',  # gare, guerre

    # Fricatives
    'f',  # fin, femme
    'v',  # vin, verre
    's',  # sa, soir
    'z',  # zone, zéro
    'ʃ',  # chat, chien
    'ʒ',  # je, jour

    # Nasals
    'm',  # main, mère
    'n',  # non, nuit
    'ɲ',  # agneau, vigne

    # Approximants/Liquids
    'l',  # long, lire
    'ʁ',  # rouge, roi (uvular)

    # Semivowels/Glides
    'j',  # yeux, fille
    'ɥ',  # huit, lui
    'w',  # oui, noir
}

french_vowels = {
    # Oral vowels (front unrounded)
    'i',  # si, vie
    'e',  # été, parler
    'ɛ',  # belle, mère
    'a',  # table, chat

    # Oral vowels (front rounded)
    'y',  # tu, rue
    'ø',  # deux, feu
    'œ',  # seul, beurre

    # Oral vowels (back)
    'u',  # tout, vous
    'o',  # beau, chaud
    'ɔ',  # homme, nord

    # Schwa
    'ə',  # le, petit

    # Nasal vowels
    'ɛ̃',  # pain, main
    'œ̃',  # un, parfum (may merge with ɛ̃)
    'ɑ̃',  # dans, temps
    'ɔ̃',  # bon, monde

    # Note: French doesn't have true diphthongs in the same sense as English
    # Sequences like /wa/, /ɥi/ are analyzed as semi-vowel + vowel
}

# SPANISH PHONEMES - BROADER TRANSCRIPTION

spanish_consonants = {
    # Plosives/Stops
    'p',  # padre, capa
    'b',  # boca, lobo (includes [β] allophone)
    't',  # toma, pata
    'd',  # dedo, nada (includes [ð] allophone)
    'k',  # casa, loco
    'ɡ',  # gato, lago (includes [ɣ] allophone)

    'ʃ',  # "sh" sound as in chico, leche (should be the affricate tʃ, but we don't do affricates over here :p

    # Fricatives
    'f',  # fuego, café
    'θ',  # cinco, caza (Peninsular)
    's',  # sol, casa
    'x',  # jamón, ojo

    # Nasals
    'm',  # madre, cama
    'n',  # nada, mano
    'ɲ',  # año, niño

    # Liquids
    'l',  # luna, ala
    'ʎ',  # llave, calle (merging with j in many dialects)
    'ɾ',  # pero, caro (tap)
    'r',  # perro, rosa (trill)

    # Approximants
    'j',  # yo, mayo
}

spanish_vowels = {
    # Five vowel system
    'i',  # piso, mí
    'e',  # mesa, té
    'a',  # casa, pan
    'o',  # toro, no
    'u',  # puro, tú
}

# PORTUGUESE PHONEMES - BROADER TRANSCRIPTION

portuguese_consonants = {
    # Plosives/Stops
    'p',  # pão, capa
    'b',  # bom, cabo
    't',  # tudo, gato
    'd',  # dar, moda
    'k',  # casa, aqui
    'ɡ',  # gato, lago

    # Fricatives
    'f',  # fogo, café
    'v',  # vinho, uva
    's',  # saber, caça
    'z',  # casa, zero
    'ʃ',  # chave, caixa
    'ʒ',  # gente, hoje

    # Nasals
    'm',  # mãe, campo
    'n',  # nada, ano
    'ɲ',  # linha, ninho

    # Liquids
    'l',  # lua, fala
    'ʎ',  # filho, palha
    'ɾ',  # caro, prato (tap)
    'ʁ',  # rio, carro (varies by dialect)
}

portuguese_vowels = {
    # Oral vowels - basic
    'i',  # filho, vir
    'e',  # medo, verde
    'ɛ',  # café, pé
    'a',  # casa, sal (BP)
    'ɐ',  # casa (EP)
    'ɔ',  # avó, pó
    'o',  # avô
    'u',  # tudo, uva
    'ɨ',  # tarde, parte (EP)

    # Nasal vowels
    'ĩ',  # sim, cinco
    'ɐ̃',  # campo, cantar
    'õ',  # bom, ontem
    'ũ',  # um, mundo
}

# Create combined sets using union operation
vowels = english_vowels | german_vowels | french_vowels | spanish_vowels | portuguese_vowels
consonants = english_consonants | german_consonants | french_consonants | spanish_consonants | portuguese_consonants

forbidden_characters = {
    'X',
    'C',
    'V',
    'G',
    'S',
    'xx',
    '*'
}
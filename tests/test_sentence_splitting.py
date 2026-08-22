import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lib.core as core
from lib.core import SessionContext


def test_get_sentences_prefers_sentence_boundaries_over_comma_and_semicolon():
    ctx = SessionContext()
    ctx.set_session('segment_test')
    session = ctx.get_session('segment_test')
    session['language'] = 'fra'
    session['translate_enabled'] = False
    session['translate'] = None
    session['tts_engine'] = 'XTTS'
    core.context = ctx

    text = (
        "Un soleil de fin de journée teintait de reflets roses la grisaille de son point culminant "
        "et s'enfonçait dans le noir vers sa base; un feu de broussailles remontait la colline sur le côté gauche de la fissure. "
        "Bosch régla son scanner sur la fréquence des services d'intervention du comté de Los Angeles "
        "et entendit les capitaines des détachements de pompiers informer le poste de commandement que neuf maisons "
        "avaient déjà été détruites dans une rue, celles de la rue voisine se trouvant maintenant sur le chemin des flammes."
    )

    segments = core.get_sentences('segment_test', text)
    assert segments, 'Expected at least one segment'

    joined = ' '.join(segment.strip() for segment in segments if segment.strip())
    assert 'rue, celles de la rue voisine' in joined
    assert 'base; un feu de broussailles' in joined

    # A forced split may legitimately land on the last comma / semicolon before a natural
    # continuation, since the user prefers that over splitting at an earlier conjunction.
    # The character cap is still enforced elsewhere by the XTTS guard; the intent here is
    # narrative rhythm, not a strict per-sentence max-length requirement.
    assert any('une rue,' in segment for segment in segments)


def test_get_sentences_does_not_force_split_inside_clause_without_punctuation():
    ctx = SessionContext()
    ctx.set_session('segment_test_no_punct')
    session = ctx.get_session('segment_test_no_punct')
    session['language'] = 'fra'
    session['translate_enabled'] = False
    session['translate'] = None
    session['tts_engine'] = 'XTTS'
    core.context = ctx

    text = (
        "Bosch régla son scanner sur la fréquence des services d'intervention du comté de Los Angeles "
        "et entendit les capitaines des détachements de pompiers informer le poste de commandement "
        "que neuf maisons avaient déjà été détruites dans une rue, celles de la rue voisine se trouvant "
        "maintenant sur le chemin des flammes."
    )

    segments = core.get_sentences('segment_test_no_punct', text)
    assert segments
    assert any('détachements de pompiers informer' in segment for segment in segments)
    assert not any('détachements' in segment and 'de pompiers' not in segment for segment in segments)


def test_get_sentences_splits_long_unpunctuated_clause_on_clause_boundaries():
    ctx = SessionContext()
    ctx.set_session('segment_test_clause_fallback')
    session = ctx.get_session('segment_test_clause_fallback')
    session['language'] = 'fra'
    session['translate_enabled'] = False
    session['translate'] = None
    session['tts_engine'] = 'XTTS'
    core.context = ctx

    text = (
        "Bosch traversa le quartier et observa les voitures immobilisées et les portes ouvertes et les habitants qui couraient "
        "vers les bus et les sirènes qui résonnaient au loin et les flammes qui montaient au-dessus des maisons et les camions "
        "de pompiers qui s'arrêtèrent devant la rue et les équipes qui se déployèrent en file indienne pour bloquer l'accès "
        "et protéger les familles encore présentes dans le voisinage."
    )

    segments = core.get_sentences('segment_test_clause_fallback', text)
    assert segments
    assert len(segments) > 1
    assert max(len(segment) for segment in segments if segment.strip()) <= core.language_mapping['fra']['max_chars']
    assert any('camions de pompiers' in segment for segment in segments)


def test_get_sentences_keeps_final_phrase_before_real_sentence_end():
    ctx = SessionContext()
    ctx.set_session('segment_test_final_phrase')
    session = ctx.get_session('segment_test_final_phrase')
    session['language'] = 'fra'
    session['translate_enabled'] = False
    session['translate'] = None
    session['tts_engine'] = 'XTTS'
    core.context = ctx

    text = (
        "C'était seulement lorsque Bosch quittait la véranda pour rentrer dans la maison que l'animal s'avançait à pas feutrés afin "
        "de s'emparer des offrandes. Harry l'avait baptisé Timido. Parfois, en pleine nuit, il entendait ses hurlements résonner au "
        "fond du canyon."
    )

    segments = core.get_sentences('segment_test_final_phrase', text)
    assert segments
    assert any("s'emparer des offrandes." in segment for segment in segments)
    assert not any("s'emparer" in segment and "des offrandes" not in segment for segment in segments)


def test_get_sentences_prefers_last_comma_over_earlier_clause_connector():
    ctx = SessionContext()
    ctx.set_session('segment_test_comma_preference')
    session = ctx.get_session('segment_test_comma_preference')
    session['language'] = 'fra'
    session['translate_enabled'] = False
    session['translate'] = None
    session['tts_engine'] = 'XTTS'
    core.context = ctx

    text = (
        "Bosch régla son scanner sur la fréquence des services d'intervention du comté de Los Angeles et "
        "entendit les capitaines des détachements de pompiers informer le poste de commandement que neuf maisons "
        "avaient déjà été détruites dans une rue, celles de la rue voisine se trouvant maintenant sur le chemin des flammes."
    )

    segments = core.get_sentences('segment_test_comma_preference', text)
    assert segments
    assert any('une rue,' in segment for segment in segments)
    assert 'celles de la rue voisine' in ' '.join(segments)
    assert not any('Los Angeles et' in segment and 'entendit' not in segment for segment in segments)


def test_get_sentences_does_not_merge_short_sentences_across_sentence_boundaries():
    ctx = SessionContext()
    ctx.set_session('segment_test_short_sentences')
    session = ctx.get_session('segment_test_short_sentences')
    session['language'] = 'fra'
    session['translate_enabled'] = False
    session['translate'] = None
    session['tts_engine'] = 'XTTS'
    core.context = ctx

    text = (
        "Il regarda l'escadrille des hélicoptères; semblables à des libellules à cette distance, "
        "ils zigzaguaient entre les nuages de fumée avant de larguer des tonnes d'eau et de retardateur "
        "de couleur rose sur les maisons et les arbres en feu. Cela lui rappela les offensives aériennes "
        "au Vietnam. Le bruit. La danse hésitante des appareils surchargés. Des masses d'eau traversaient "
        "des toits en feu, de la vapeur s'élevant aussitôt dans le ciel."
    )

    segments = core.get_sentences('segment_test_short_sentences', text)
    assert segments
    assert any(segment.strip() == 'Le bruit.' for segment in segments)
    assert any(segment.strip() == 'La danse hésitante des appareils surchargés.' for segment in segments)
    assert not any('en feu. Cela' in segment for segment in segments)
    assert not any('Vietnam. Le bruit.' in segment for segment in segments)
    assert not any('Le bruit. La danse' in segment for segment in segments)

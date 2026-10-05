# Interludes: the music generated between chapters (lib/classes/interlude_generator.py, core.generate_interludes(),
# core.combine_audio_chapters()). Everything here stays English, whatever the book's language: MusicGen understands
# English descriptions best, and the multilingual classifier compares the book's text with these English sentences.

interlude_duration_range = (20, 30) # seconds, MusicGen generates 30 s at most
interlude_fade_in_range = (5.0, 10.0) # seconds of fade in before the chapter's last sentence ends
interlude_fade_out_range = (4.0, 6.0) # seconds of fade out after the next chapter starts
interlude_classifier_repo = 'MoritzLaurer/mDeBERTa-v3-base-mnli-xnli' # multilingual zero-shot (NLI) classifier
interlude_genre_min_score = 0.10 # averaged score the winning genre needs (26 genres: 0.04 is a random guess), else 'neutral' instruments

# zero-shot classifier sentences, {} is the genre, the mood family or the mood
interlude_templates = {
    'genre': 'This book belongs to the {} genre.',
    'family': 'The mood of this passage is {}.',
    'mood': 'This passage evokes {}.'
}

# 128 moods in 16 families of 8: the family is picked first, then the mood inside it (16 + 8 classifier passes
# per interlude instead of 128). Each mood is (emotion and tempo, cinematic style, percussion); the melodic
# instruments come from the book genre, so the same mood sounds like a thriller in a thriller and like a fairy
# tale in a fairy tale. The original five moods live on inside their families: action and suspense, melancholic and
# emotional, peaceful and ambient, epic and orchestral, sci-fi and electronic.
# 'beatless' is used instead of 'no percussion': MusicGen's text encoder does not handle negations
interlude_moods = {
    'calm and peaceful': {
        'a tranquil dawn': ('serene, slow tempo, soft sustained chords, gentle rising melody', 'cinematic ambient score', 'beatless'),
        'the pastoral countryside': ('relaxed, slow tempo, airy pastoral melody, light ornaments', 'gentle cinematic underscore', 'soft hand percussion'),
        'quiet contemplation': ('still, very slow tempo, sparse notes, long pauses', 'minimalist cinematic score', 'beatless'),
        'a lullaby': ('soothing, slow lullaby in three, soft and tender', 'intimate cinematic underscore', 'beatless'),
        'a still night': ('hushed nocturne, slow tempo, distant soft tones', 'atmospheric cinematic score', 'faint distant timpani rolls'),
        'serene water': ('flowing, calm, gentle rippling arpeggios', 'cinematic ambient score', 'soft shakers'),
        'cozy warmth at home': ('warm, cozy, unhurried, soft major harmonies', 'heartwarming cinematic underscore', 'light brushed percussion'),
        'peaceful and ambient': ('relaxing, calm background music, soft acoustic guitar, relaxing nature sounds', 'ambient cinematic score', 'lo-fi beats')
    },
    'joyful and uplifting': {
        'carefree joy': ('bright, upbeat, light bouncy rhythm, major key', 'feel-good cinematic score', 'claps and light drums'),
        'a festive celebration': ('festive, lively tempo, celebratory rhythm', 'joyful cinematic score', 'festive percussion and tambourine'),
        'bright optimism': ('optimistic, medium tempo, rising major melody', 'uplifting cinematic score', 'steady light drums'),
        'warm friendship': ('warm, friendly, heartfelt major melody, medium tempo', 'heartwarming cinematic score', 'soft brushed drums'),
        'a joyful reunion': ('joyous, swelling, emotional uplift, major key', 'emotional cinematic score', 'swelling cymbals and timpani'),
        'springtime renewal': ('fresh, light, blossoming melody, medium tempo', 'bright cinematic score', 'light shakers'),
        'exuberant dancing': ('exuberant, fast dance rhythm, energetic', 'lively cinematic score', 'driving dance percussion'),
        'a hopeful new beginning': ('hopeful, gradually building, uplifting major key', 'inspirational cinematic score', 'building toms and cymbal swells')
    },
    'romantic and tender': {
        'first love': ('tender, innocent, sweet melody, medium slow tempo', 'romantic cinematic score', 'beatless'),
        'intimate tenderness': ('intimate, soft, delicate, slow tempo', 'intimate cinematic underscore', 'beatless'),
        'longing': ('yearning, slow, aching melody, suspended chords', 'emotional cinematic score', 'soft heartbeat pulse'),
        'passionate romance': ('passionate, sweeping melody, swelling dynamics', 'lush romantic cinematic score', 'timpani swells'),
        'bittersweet love': ('bittersweet, slow, shifting between minor and major', 'emotional cinematic score', 'beatless'),
        'devotion': ('devoted, warm, stately slow tempo, heartfelt', 'romantic cinematic score', 'gentle timpani'),
        'flirtatious charm': ('playful, charming, light swing, coy', 'romantic comedy score', 'brushed snare and finger snaps'),
        'lovers reunited': ('emotional, soaring, building to a warm climax', 'sweeping cinematic score', 'cymbal swells and timpani')
    },
    'melancholic and sad': {
        'grief': ('grieving, very slow, heavy minor chords, mournful', 'mournful cinematic score', 'beatless'),
        'loneliness': ('lonely, sparse, slow solitary melody, empty space', 'minimalist cinematic score', 'beatless'),
        'heartbreak': ('heartbroken, slow, aching minor melody', 'emotional cinematic score', 'distant low drum'),
        'melancholic and emotional': ('melancholic, slow piano, melancholic cello, ambient reverb', 'emotional cinematic score', 'beatless'),
        'rainy melancholy': ('melancholic, slow, soft falling patterns, grey mood', 'atmospheric cinematic score', 'soft rain-like brushes'),
        'a farewell': ('wistful farewell, slow, gently fading', 'bittersweet cinematic score', 'beatless'),
        'despair': ('despairing, dark, slow, heavy, hopeless', 'dark cinematic score', 'slow heavy low drums'),
        'resignation': ('resigned, quiet, slow, descending phrases', 'subdued cinematic underscore', 'beatless')
    },
    'nostalgic and reflective': {
        'childhood memories': ('nostalgic, innocent, music box like, gentle', 'tender cinematic score', 'soft glockenspiel ticks'),
        'bittersweet nostalgia': ('bittersweet, warm, slow, wistful', 'nostalgic cinematic score', 'beatless'),
        'looking back on life': ('reflective, introspective, medium slow tempo', 'contemplative cinematic score', 'soft brushed drums'),
        'faded photographs': ('faded, hazy, warm lo-fi texture, slow', 'dreamy cinematic underscore', 'dusty lo-fi beat'),
        'autumn reflection': ('autumnal, mellow, golden warmth, slow', 'warm cinematic score', 'light hand percussion'),
        'letters from the past': ('tender, intimate, reminiscent, slow', 'intimate cinematic score', 'beatless'),
        'the passing of time': ('contemplative, steady pulse, timeless', 'reflective cinematic underscore', 'clock-like ticking percussion'),
        'a wistful daydream': ('dreamy, floating, soft haze, slow', 'ethereal cinematic score', 'beatless')
    },
    'mysterious and curious': {
        'an enigmatic puzzle': ('enigmatic, curious, unresolved harmonies, medium tempo', 'mystery cinematic score', 'light ticking percussion'),
        'a secret discovery': ('mysterious, building curiosity, shimmering textures', 'cinematic discovery score', 'soft mallets and cymbal swells'),
        'a foggy unknown': ('foggy, ambiguous harmonies, hazy atmosphere, slow', 'atmospheric cinematic score', 'distant low drums'),
        'an investigation': ('investigative, steady pulse, curious motif', 'detective cinematic score', 'muted snare pulse'),
        'hidden clues': ('sneaky, light staccato, inquisitive', 'mystery cinematic underscore', 'woodblock and light shakers'),
        'curious exploration': ('curious, wandering melody, medium tempo', 'adventurous cinematic underscore', 'light hand drums'),
        'a strange encounter': ('uncanny, unusual intervals, sparse', 'eerie cinematic score', 'sparse metallic hits'),
        'ancient secrets': ('ancient, modal, mysterious drones, slow', 'mystical cinematic score', 'deep frame drum')
    },
    'suspense and tension': {
        'creeping dread': ('creeping, slowly building tension, low pulses', 'suspense cinematic score', 'low heartbeat drum'),
        'a ticking clock': ('urgent, rising tension', 'thriller cinematic score', 'ticking clock percussion'),
        'stealth': ('stealthy, quiet, tiptoeing rhythm', 'suspense cinematic underscore', 'muted rimshots'),
        'an interrogation': ('tense, sparse, cold, unresolved', 'tense cinematic underscore', 'sparse low hits'),
        'impending danger': ('ominous build, rising tension, swelling', 'suspense cinematic score', 'rolling timpani and taiko'),
        'paranoia': ('anxious, unstable rhythm, dissonant', 'psychological thriller score', 'irregular glitchy percussion'),
        'nervous anticipation': ('nervous, restless pulse, held breath', 'tense cinematic score', 'fast muted hi-hat pulse'),
        'a cliffhanger': ('tense crescendo, suspended, unresolved ending', 'dramatic cinematic score', 'snare roll and final boom')
    },
    'fear and horror': {
        'terror': ('terrifying, harsh dissonance, sudden stabs', 'horror cinematic score', 'violent hits and booms'),
        'a haunted house': ('eerie, creaking textures, ghostly', 'horror cinematic score', 'distant knocking percussion'),
        'a lurking monster': ('menacing, low growling drones, slow', 'dark horror score', 'heavy slow thuds'),
        'a nightmare': ('nightmarish, distorted, disorienting', 'surreal horror score', 'reversed percussion'),
        'panic': ('panicked, fast, frantic, chaotic', 'horror chase score', 'frantic pounding drums'),
        'eerie silence': ('eerie near silence, thin high tones', 'minimal horror underscore', 'beatless'),
        'a curse': ('cursed, dark ritualistic, slow minor', 'occult cinematic score', 'ritual drums'),
        'psychological horror': ('unsettling, detuned, creeping, claustrophobic', 'psychological horror score', 'irregular heartbeat thumps')
    },
    'action and chase': {
        'a high speed chase': ('fast tempo, driving rhythm, adrenaline', 'action cinematic score', 'driving drums and taiko'),
        'an escape': ('urgent, fast, breathless momentum', 'action cinematic score', 'pounding percussion'),
        'a heist': ('cool, rhythmic, slick groove, tension', 'heist movie score', 'tight funky drums'),
        'a fight': ('aggressive, hard hitting, fast', 'action cinematic score', 'hard-hitting drums and impacts'),
        'a pursuit through the city': ('relentless, pulsing, fast tempo', 'urban action score', 'relentless electronic drums'),
        'a race against time': ('racing, accelerating, high energy', 'action cinematic score', 'accelerating drum ostinato'),
        'a rooftop run': ('agile, fast, syncopated rhythm', 'action cinematic score', 'syncopated percussion'),
        'action and suspense': ('fast tempo, tense strings, dramatic', 'dramatic trailer music', 'cinematic percussion')
    },
    'battle and conflict': {
        'war drums': ('marching rhythm, martial, relentless', 'epic war score', 'thunderous war drums'),
        'a siege': ('heavy, relentless, brooding power', 'epic battle score', 'heavy taiko and timpani'),
        'a clash of armies': ('massive, chaotic, epic battle intensity', 'epic battle score', 'massive percussion ensemble'),
        'a duel': ('tense, focused, rhythmic clashes', 'cinematic duel score', 'sharp percussive hits'),
        'the aftermath of battle': ('somber, slow, devastated, mournful', 'elegiac cinematic score', 'distant slow drum'),
        'a rebellion': ('defiant, rising, driving rhythm', 'epic cinematic score', 'driving snare and toms'),
        'a call to arms': ('rallying, heroic fanfare, stirring', 'heroic cinematic score', 'military snare and timpani'),
        'a last stand': ('desperate, heroic, intense, climactic', 'epic cinematic score', 'pounding taiko and timpani')
    },
    'epic and heroic': {
        "a hero's journey": ('adventurous heroic theme, building', 'epic adventure score', 'rhythmic orchestral percussion'),
        'a quest beginning': ('adventurous, hopeful, setting out, medium tempo', 'adventure cinematic score', 'marching snare'),
        'epic and orchestral': ('epic, 120 bpm, massive brass, epic choir, soaring strings', 'hans zimmer style cinematic score', 'thunderous orchestral percussion'),
        'a noble sacrifice': ('noble, slow, heartbreaking grandeur', 'emotional epic score', 'slow timpani'),
        'a rising hero': ('ascending, inspiring, building to a climax', 'epic cinematic score', 'building drums and cymbal crashes'),
        'vast landscapes': ('majestic, wide open, slow and sweeping', 'sweeping cinematic score', 'soft timpani rolls'),
        'an ancient kingdom': ('regal, stately, ancient grandeur', 'epic historical score', 'ceremonial drums'),
        'destiny': ('fateful, powerful, building intensity', 'epic cinematic score', 'pounding orchestral drums')
    },
    'triumphant and victorious': {
        'victory': ('triumphant, bold, celebratory fanfare', 'triumphant cinematic score', 'triumphant timpani and cymbals'),
        'triumph over adversity': ('triumphant, emotional, soaring', 'uplifting epic score', 'building drums'),
        'a coronation': ('regal, majestic, ceremonial', 'ceremonial cinematic score', 'ceremonial timpani'),
        "a hero's homecoming": ('warm, triumphant, emotional', 'heartfelt cinematic score', 'gentle march drums'),
        'an achievement': ('proud, bright, uplifting', 'uplifting cinematic score', 'steady drums'),
        'a rescue': ('relieved, rising, joyful release', 'rescue cinematic score', 'cymbal swell and timpani'),
        'sunrise after the storm': ('hopeful, gradually brightening, radiant', 'radiant cinematic score', 'soft timpani swells'),
        'a happy ending': ('resolved, warm, satisfying final cadence', 'heartwarming cinematic finale', 'gentle cymbal swell')
    },
    'dark and ominous': {
        'a looming threat': ('ominous, low, slow, heavy', 'dark cinematic score', 'slow ominous booms'),
        'a villain': ('sinister, menacing theme, dark', 'villain cinematic score', 'heavy low drums'),
        'a dark ritual': ('ritualistic, chant like, dark', 'occult cinematic score', 'tribal ritual drums'),
        'corruption': ('decaying, dissonant, slowly twisting', 'dark cinematic underscore', 'distorted low hits'),
        'a gathering storm': ('brooding, rumbling, building', 'dark epic score', 'rumbling timpani'),
        'oppression': ('oppressive, cold, mechanical, bleak', 'dystopian cinematic score', 'mechanical industrial percussion'),
        'betrayal': ('shocking, bitter, dark turn', 'dramatic cinematic score', 'sudden impact hit'),
        'menace': ('threatening, stalking pulse, dark', 'dark thriller score', 'stalking low drum pulse')
    },
    'wonder and magical': {
        'an enchanted forest': ('enchanted, shimmering, magical, gentle', 'fantasy cinematic score', 'soft chimes and bells'),
        'a fairy tale': ('storybook, whimsical, magical', 'fairy tale cinematic score', 'light glockenspiel and triangle'),
        'a magic spell': ('sparkling, mystical, rising shimmer', 'magical cinematic score', 'shimmering chimes and cymbal swell'),
        'a new world discovered': ('awe inspiring, wide, blossoming', 'sweeping cinematic score', 'soft timpani rolls'),
        'a starry sky': ('cosmic, twinkling, vast, slow', 'space ambient cinematic score', 'beatless'),
        'a dreamlike fantasy': ('dreamlike, floating, ethereal', 'ethereal cinematic score', 'beatless'),
        'mythical creatures': ('majestic, mysterious, wondrous', 'fantasy cinematic score', 'deep tribal drums'),
        'sci-fi and electronic': ('futuristic, atmospheric synth pads, pulsing bass', 'blade runner vibe cinematic score', 'synthwave drums')
    },
    'playful and humorous': {
        'mischief': ('mischievous, sneaky playful staccato', 'comedy cinematic score', 'light woodblocks'),
        'whimsy': ('whimsical, light, quirky', 'whimsical film score', 'light toy percussion'),
        'slapstick comedy': ('comedic, bouncy, exaggerated', 'cartoon comedy score', 'slapstick percussion hits'),
        'light-hearted banter': ('light, breezy, conversational rhythm', 'light comedy score', 'brushed snare'),
        'a quirky character': ('quirky, odd meter, playful', 'quirky film score', 'odd meter claps'),
        'a cheeky prank': ('cheeky, tiptoeing, playful', 'comedy cinematic underscore', 'tiptoe woodblock'),
        'cartoonish antics': ('cartoonish, zany, fast', 'cartoon score', 'zany xylophone and drum hits'),
        'bouncy fun': ('bouncy, upbeat, fun', 'feel-good film score', 'bouncy drums and claps')
    },
    'solemn and spiritual': {
        'a funeral': ('solemn, slow funeral march, grave', 'solemn cinematic score', 'muffled funeral drum'),
        'a prayer': ('prayerful, slow, reverent', 'sacred cinematic score', 'beatless'),
        'a sacred ritual': ('sacred, chant like, timeless', 'spiritual cinematic score', 'slow ritual frame drum'),
        'redemption': ('redemptive, slowly rising, emotional release', 'emotional cinematic score', 'gentle timpani swell'),
        'forgiveness': ('gentle, warm, healing', 'heartfelt cinematic score', 'beatless'),
        'mortality': ('contemplative, slow, profound', 'elegiac cinematic score', 'distant slow drum'),
        'a cathedral': ('reverberant, majestic, sacred', 'sacred cinematic score', 'deep cathedral bell'),
        'transcendence': ('transcendent, ethereal, ascending', 'ethereal cinematic score', 'soft cymbal swells')
    }
}

# book genre: (instruments, mood families it favours). The instruments go into every prompt of the book, the
# favoured families weigh 1.3x when the family is picked
interlude_genre_styles = {
    'fantasy': ('orchestral, celtic harp, flutes, choir, folk instruments', ['wonder and magical', 'epic and heroic', 'battle and conflict']),
    'science fiction': ('synthesizers, electronic textures, ambient pads, futuristic sound design', ['wonder and magical', 'mysterious and curious', 'suspense and tension']),
    'cyberpunk and dystopian': ('dark synthwave, industrial textures, distorted bass, cold electronics', ['dark and ominous', 'action and chase', 'suspense and tension']),
    'horror': ('dissonant strings, low drones, prepared piano, unsettling sound design', ['fear and horror', 'dark and ominous', 'suspense and tension']),
    'gothic': ('pipe organ, harpsichord, dark strings, choir', ['dark and ominous', 'mysterious and curious', 'melancholic and sad']),
    'thriller': ('dark cinematic score, pulsing synth bass, staccato strings', ['suspense and tension', 'action and chase', 'dark and ominous']),
    'mystery and detective': ('pizzicato strings, muted piano, clarinet, soft percussion', ['mysterious and curious', 'suspense and tension']),
    'crime and noir': ('smoky jazz, muted trumpet, upright bass, brushed drums', ['dark and ominous', 'suspense and tension', 'mysterious and curious']),
    'romance': ('piano, warm strings, acoustic guitar', ['romantic and tender', 'joyful and uplifting', 'melancholic and sad']),
    'historical fiction': ('chamber strings, harpsichord, period instruments', ['nostalgic and reflective', 'epic and heroic', 'romantic and tender']),
    'war': ('military snare, brass, low strings, timpani', ['battle and conflict', 'melancholic and sad', 'solemn and spiritual']),
    'western': ('acoustic guitar, harmonica, whistling, banjo', ['action and chase', 'nostalgic and reflective', 'calm and peaceful']),
    'adventure': ('full orchestra, bold brass, adventurous percussion', ['epic and heroic', 'action and chase', 'wonder and magical']),
    'mythology and fairy tales': ('harp, celesta, woodwinds, enchanted orchestra', ['wonder and magical', 'epic and heroic', 'playful and humorous']),
    "children's": ('glockenspiel, ukulele, pizzicato strings, toy piano', ['playful and humorous', 'joyful and uplifting', 'wonder and magical']),
    'young adult': ('indie instrumental, piano, light electronic beats', ['joyful and uplifting', 'romantic and tender', 'suspense and tension']),
    'literary fiction': ('solo piano, chamber strings, minimalist', ['nostalgic and reflective', 'melancholic and sad', 'calm and peaceful']),
    'comedy and humor': ('bouncy pizzicato, bassoon, light percussion', ['playful and humorous', 'joyful and uplifting']),
    'drama': ('piano and strings, cinematic', ['melancholic and sad', 'romantic and tender', 'nostalgic and reflective']),
    'biography and memoir': ('acoustic guitar, gentle piano, soft strings, documentary style', ['nostalgic and reflective', 'triumphant and victorious']),
    'history': ('documentary orchestral score, strings, timpani', ['epic and heroic', 'solemn and spiritual', 'nostalgic and reflective']),
    'religion and spirituality': ('ambient pads, choir, singing bowls', ['solemn and spiritual', 'calm and peaceful']),
    'philosophy': ('minimalist piano, ambient strings', ['calm and peaceful', 'nostalgic and reflective', 'mysterious and curious']),
    'science and nature': ('documentary score, ambient pads, marimba, organic textures', ['wonder and magical', 'calm and peaceful', 'mysterious and curious']),
    'self-help and business': ('modern ambient, light piano, soft electronic pulse', ['joyful and uplifting', 'calm and peaceful', 'triumphant and victorious']),
    'poetry': ('sparse piano, solo cello, intimate', ['calm and peaceful', 'melancholic and sad', 'romantic and tender'])
}

# ISO 639-1 codes of the ~100 languages the classifier's mDeBERTa base was pretrained on (CC100): other languages
# are read without failing but scored at random, so their chapters get interlude_neutral_moods instead
interlude_classifier_languages = {
    'af', 'am', 'ar', 'as', 'az', 'be', 'bg', 'bn', 'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et',
    'eu', 'fa', 'fi', 'fr', 'fy', 'ga', 'gd', 'gl', 'gu', 'ha', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jv',
    'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'la', 'lo', 'lt', 'lv', 'mg', 'mk', 'ml', 'mn', 'mr', 'ms', 'my', 'nb', 'ne',
    'nl', 'nn', 'no', 'om', 'or', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'sa', 'sd', 'si', 'sk', 'sl', 'so', 'sq', 'sr', 'su',
    'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'ug', 'uk', 'ur', 'uz', 'vi', 'xh', 'yi', 'zh'
}

# unclassifiable text: neutral instruments (unless the genre is known) and calm, reflective moods in turn
interlude_neutral_style = ('piano and strings, cinematic, understated', [])
interlude_neutral_moods = [
    ('nostalgic and reflective', 'the passing of time'),
    ('calm and peaceful', 'quiet contemplation'),
    ('nostalgic and reflective', 'a wistful daydream'),
    ('calm and peaceful', 'a still night'),
    ('nostalgic and reflective', 'autumn reflection'),
    ('calm and peaceful', 'serene water'),
    ('nostalgic and reflective', 'looking back on life'),
    ('calm and peaceful', 'peaceful and ambient')
]

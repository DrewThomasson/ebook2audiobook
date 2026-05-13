import re
from collections import Counter

class QuoteTagger:

    def tag(self, toks):

        predictions = []
        currentQuote = []
        curStartTok = None
        lastPar = None

        quote_symbols = Counter()

        # Count all possible quote types including French guillemets
        for tok in toks:
            if tok.text in ["“", "”", "\""]:
                quote_symbols["DOUBLE_QUOTE"] += 1
            elif tok.text in ["‘", "’", "'"]:
                quote_symbols["SINGLE_QUOTE"] += 1
            elif tok.text in ["«", "»"]:
                quote_symbols["GUILLEMET"] += 1
            elif tok.text == "—":
                quote_symbols["DASH"] += 1

        quote_symbol = "DOUBLE_QUOTE"
        if len(quote_symbols) > 0:
            quote_symbol = quote_symbols.most_common()[0][0]

        # Helper function to check if a token matches the chosen quote symbol
        def is_quote_symbol(token_text, symbol):
            if symbol == "DOUBLE_QUOTE":
                return token_text in ["“", "”", "\""]
            elif symbol == "SINGLE_QUOTE":
                return token_text in ["‘", "’", "'"]
            elif symbol == "GUILLEMET":
                return token_text in ["«", "»"]
            elif symbol == "DASH":
                return token_text == "—"
            return False

        for tok in toks:
            w = tok.text

            # Normalize quote symbol for this token
            for w_idx, w_char in enumerate(w):
                if w_char in ["“", "”", "\""]:
                    w = "DOUBLE_QUOTE"
                elif w_char in ["‘", "’", "'"]:
                    if w_idx == 0:
                        suff = w[w_idx+1:]
                        if suff not in ["s", "d", "ll", "ve"]:
                            w = "SINGLE_QUOTE"
                elif w_char in ["«", "»"]:
                    w = "GUILLEMET"
                elif w_char == "—":
                    w = "DASH"

            # start over at each new paragraph
            if tok.paragraph_id != lastPar and lastPar is not None:
                if len(currentQuote) > 0:
                    predictions.append((curStartTok, tok.token_id-1))
                curStartTok = None
                currentQuote = []

            # Detect start or end of quote
            if is_quote_symbol(tok.text, quote_symbol):
                if curStartTok is not None:
                    if len(currentQuote) > 0:
                        predictions.append((curStartTok, tok.token_id))
                        currentQuote.append(tok.text)
                    curStartTok = None
                    currentQuote = []
                else:
                    curStartTok = tok.token_id

            if curStartTok is not None:
                currentQuote.append(tok.text)

            lastPar = tok.paragraph_id

        for start, end in predictions:
            for i in range(start, end+1):
                toks[i].inQuote = True

        return predictions
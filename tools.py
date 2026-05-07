import re

def calculator(query):
    try:
        return str(eval(query))
    except:
        return "Invalid calculation"


def web_search(query):
    # dummy fallback (later API add kar sakte ho)
    return f"Web result for: {query}"
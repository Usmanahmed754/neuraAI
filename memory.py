def build_history(messages):
    text = ""
    for msg in messages:
        text += f"{msg['role']}: {msg['content']}\n"
    return text
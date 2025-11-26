import os
import openai
import aiohttp
import asyncio


API_URL = "http://localhost:1234/v1/chat/completions"
API_KEY = "no-key-required"   # LM Studio doesn’t need it

SEMAPHORE = asyncio.Semaphore(3)   # limit to 3 parallel API calls

def clean_for_csv(text):
    if not text:
        return ''

    # 1. Alles in String umwandeln
    text = str(text)

    # 2. Neue Zeilen, Carriage Returns, Tabs → Leerzeichen
    text = text.replace('\n', '#').replace('\r', '#').replace('\t', '#')

    # 3. Unsichtbare Unicode-Zeichen entfernen
    text = text.replace('\u00A0', '#')  # NBSP → Leerzeichen
    text = text.replace('\u200B', '')  # Zero-width space löschen

    # 4. Anführungszeichen entfernen
    text = text.replace('"', '')

    # 5. Kommas optional ersetzen, falls nötig (z. B. Pipe)
    text = text.replace(',', '#')

    # 6. Mehrfach-Leerzeichen auf eins reduzieren und trimmen
    text = ' '.join(text.split())

    return text

# -----------------------------
# Generic async request
# -----------------------------
async def lmstudio_request(session: aiohttp.ClientSession, question: str, model="dein-modell-name"):
    """
    Sends a prompt to the LM Studio API asynchronously.
    """

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.1,
        "max_tokens": 150
    }

    async with SEMAPHORE:   # only 3 requests at a time
        try:
            async with session.post(API_URL, json=payload, timeout=60) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]

        except Exception as e:
            return f"Error: {e}"


# -----------------------------
# Specific wrapper: send_prompt
# -----------------------------
async def send_prompt(session, question: str):
    return await lmstudio_request(session, question)


# -----------------------------
# Specific wrapper: extract_company
# -----------------------------
async def set_prompt_text(session, text: str):

    question_mistral = (
        f"Suche nach möglichen Zeitstempeln und gibt nur dessen Jahreszahl (YYYY) aus, bei mehrfachtreffern das nur die jüngste jahreszahl ausgeben. Gültige Jahre sind nur zwischen 1900 und 2100. Antwortformat ist 'Year': {text}"
    )


    # question_openai = (
    #     "Gebe den Firmennamen, Unternehmensnamen, Markennamen, Personennamen "
    #     "oder etwas mit einem Titel wie Ing. oder Dip. aus, den du im folgenden findest. "
    #     "Ignoriere Teile. Gebe nichts aus, wenn du keine Treffer findest und gebe keine "
    #     "weiteren Meldungen von deiner Seite aus: "
    #
    #     "Ignoriere folgende alleinstehenden Abkürzungen: AMI, AMD, WE, KG, OG, DG"
    # )

    # question_qwen = (
    #     "Gebe den Firmennamen und Personennamen aus,"
    #     "oder etwas mit einem Titel wie Ing. oder Dip. aus, den du im folgenden findest. Gebe nichts aus, wenn du unsicher bist oder nichts findest."
    #     "Behalte die Schreibweise bei. Ignoriere Teile. Ignoriere Zahlen und Nummerierungen. Ignoriere Treffer mit Unterstrich. Gebe ausschließlich den Namen zurück ohne weiteren Text: "
    #     f"{text} "
    # )

    # question_qwen = (
    #     "Gebe den Firmennamen im Text aus. Die Firmennamen duerfen keinen Unterstrich und keine Zahlen enthalten."
    #     "Behalte die Schreibweise bei. Ignoriere Teile. Ignoriere Treffer mit Bindestrich. Gebe ausschließlich den Namen zurück ohne weiteren Text und ohne Zahlen und ohne Unterstrich und ohne Nummerierung: "
    #     f"{text} "
    # )



    raw = await lmstudio_request(session, question_mistral)
    return clean_for_csv(raw)


# -----------------------------
# MAIN
# -----------------------------
async def main():
    async with aiohttp.ClientSession() as session:

        # print("Sending test prompt...")
        # answer1 = await send_prompt(session, "Wie heisst die Landeshauptstadt von Hessen?")
        # print(answer1)

        print("\nExtracting year...")
        answer1 = await set_prompt_text(
            session,
            "1904_7.3_EG_20090812.pdf 1900 WE 1904 7. Gebäude-, Grundstückszustand 7.3. Flächenberechnung von 1975 nach DIN 277-BGF/BRI und nach gif 1904_7.3_EG_20090812"
        )
        print(answer1)

        print("\nExtracting year...")
        answer2 = await set_prompt_text(
            session,
            "1904_7.3_EG_20090812.pdf 1900 WE 1904 7. Gebäude-, Grundstückszustand 7.3. Flächenberechnung nach DIN 277-BGF/BRI und nach gif 1904_7.3_EG_20090812"
        )
        print(answer2)

        print("\nExtracting year...")
        answer3 = await set_prompt_text(
            session,
            "Rights of Light - Basic Information.doc 373 WE 0047 5. Weitere Rechte und Ansprüche Dritter 5.2. Nachbarschaftsvereinbarungen WE"
        )
        print(answer3)



if __name__ == "__main__":
    asyncio.run(main())
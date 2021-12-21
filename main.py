import logging
import sys
import os
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from Word import Word
from AnkiConnect import create_deck, upload_media_file, media_file_exists, create_note_card, sync
from duolingo import Duolingo, DuolingoException
from configparser import ConfigParser

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
urllib_log = logging.getLogger("urllib3")
urllib_log.setLevel(logging.WARN)
gtts_log = logging.getLogger("gtts")
gtts_log.setLevel(logging.WARN)

# Check Settings
config_settings = ConfigParser()
config_settings.read("settings.ini")

# Defaults
TARGET_LANGUAGE = "en"
PARENT_DECK = False
DECK_TYPE = None
FONT = "arial"
SIZE = 200
KEEP_AUDIO = False
KEEP_IMAGE = False

if not config_settings.getboolean("DEFAULT", "enabled"):
    USERNAME = input("Duolingo Username: ")
    PASSWORD = input("Duolingo Password: ")
    LANGUAGE = input("Language: ")
    TARGET_LANGUAGE = input("Output Language: ")
    ANKI_UPLOAD = bool(input("Upload Via Anki Connect(true/false): "))
    if ANKI_UPLOAD:
        PARENT_DECK = bool(input("Create Parent Language Deck(true/false): "))
        DECK_TYPE = input("Deck Type(Basic/Basic (and reversed card)): ")
        if DECK_TYPE not in ["Basic", "Basic (and reversed card)"]:
            logging.error("Invalid Deck Type! Must Be Basic or Basic (and reversed card)")
            sys.exit(0)
        KEEP_AUDIO = bool(input("Keep Audio File After Upload(true/false): "))
        KEEP_IMAGE = bool(input("Keep Image File After Upload(true/false): "))
else:
    USERNAME = config_settings["CREDENTIALS"]["username"]
    PASSWORD = config_settings["CREDENTIALS"]["password"]
    LANGUAGE = config_settings["CREDENTIALS"]["language"]
    TARGET_LANGUAGE = config_settings["CREDENTIALS"]["translation_language"]
    FONT = config_settings["CARDS"]["font"]
    SIZE = config_settings["CARDS"].getint("size")
    ANKI_UPLOAD = config_settings.getboolean("UPLOAD", "anki_connect")
    if ANKI_UPLOAD:
        PARENT_DECK = config_settings["UPLOAD"].getboolean("create_parent_language_deck")
        DECK_TYPE = config_settings["UPLOAD"]["deck_type"]
        KEEP_AUDIO = config_settings["UPLOAD"].getboolean("keep_audio_after_upload")
        KEEP_IMAGE = config_settings["UPLOAD"].getboolean("keep_image_after_upload")

# Create The Duolingo Client
try:
    duolingo_client = Duolingo(USERNAME, PASSWORD)
    logging.info("Logged In Successfully...")
except DuolingoException as e:
    logging.error(e)
    sys.exit(0)

# Get Language Abbreviation
LANGUAGE_ABR = duolingo_client.get_abbreviation_of(LANGUAGE)

# Get Known Topics
topics = duolingo_client.get_known_topics(lang=LANGUAGE_ABR)
logging.info("Pulled Known Topics...")

# Get Known Words
vocab = duolingo_client.get_vocabulary(language_abbr=LANGUAGE_ABR)
words = vocab["vocab_overview"]
logging.info("Pulled Words..")

decks = {topic: [] for topic in topics}
word_list = []
words_to_translation = []

logging.info("Parsing Words...")
# Parse And Sort Words
for word in words:
    skill = word["skill"]
    normalized_string = word["normalized_string"].strip()
    word_string = word["word_string"]
    audio_filename = normalized_string + ".mp3"
    image_filename = normalized_string + ".png"

    # Create Temp Word
    temp_word = Word(normalized_string, word_string, skill, audio_filename, image_filename)

    # Create Media File Paths
    audio_path = os.path.join(os.getcwd(), "Decks\\Audio_Files\\",  temp_word.audio_file)
    image_path = os.path.join(os.getcwd(), "Decks\\Image_Files\\",  temp_word.image_file)

    logging.debug("Skill: {}".format(temp_word.skill))
    logging.debug("Normalized Word: {}".format(temp_word.normalized_word))
    logging.debug("Word: {}".format(temp_word.word_string))
    logging.debug("Audio File: {}".format(temp_word.audio_file))
    logging.debug("Image File: {}".format(temp_word.image_file))

    # Create Audio File If It Doesn't Exist
    if not os.path.exists(audio_path):
        try:
            audio_file = gTTS(text=word_string, lang="ja", slow=False)
            audio_file.save(audio_path)
        except OSError as e:
            logging.error("Invalid Word: {}".format(word))
            continue

    # Create Image File If It Doesn't Exist
    if not os.path.exists(image_path):
        with open(image_path, "wb") as image_file:
            img = Image.new('RGB', (1000, 1000), (255, 255, 255))
            d = ImageDraw.Draw(img)
            font = ImageFont.truetype(font=FONT, size=SIZE, encoding="UTF-16")

            # Gets Text Size And Draws Text
            text_width, text_height = d.textsize(word_string, font=font)
            d.text((0, 0), word_string, fill=(0, 0, 0), font=font)

            # Crops Image
            img = img.crop((0, 0, text_width, text_height))

            # Saves And Closes The File
            img.save(image_file)
            image_file.close()

    word_list.append(temp_word)
    words_to_translation.append(word_string)

# Pull Translations
translations = duolingo_client.get_translations(words_to_translation, source=LANGUAGE_ABR, target=TARGET_LANGUAGE)
for word in word_list:
    # Add Translation To Word Object
    translation = translations[word.word_string]
    word.translation = ",".join(translation)

    # Add Word To Skill Dictionary
    try:
        decks[word.skill].append(word)
    except KeyError:
        decks[word.skill] = [word]

if ANKI_UPLOAD:
    # Create Decks For Words
    logging.info("Creating Decks...")
    for topic in decks.keys():
        if PARENT_DECK:
            deck_name = LANGUAGE + "::" + str(topic).replace(" ", "_")
        else:
            deck_name = str(topic).replace(" ", "_")
        create_deck(deck_name)

# Create CSVs For Skills
logging.info("Creating CSVs...")
for topic in decks.keys():
    filename = "Decks/" + str(topic).replace(" ", "_") + ".csv"
    with open(filename, "w", encoding="UTF-8") as f:
        for word in decks[topic]:
            # Create Tag For Organization
            tags = LANGUAGE + "::" + str(topic).replace(" ", "_")

            # Create Front Of Card
            image_media = r'<img src="' + str(word.image_file) + '">'
            audio_media = r'[sound:' + str(word.audio_file) + ']'
            card_front = r"{}<br>{}".format(image_media, audio_media)

            # Create The Text On The Back Of The Card
            card_back = word.translation.replace(",", r"<br>")

            # Write The Values To The CSV
            f.write(card_front + ",")
            f.write(card_back + ",")
            f.write(tags + "\n")
            f.flush()

            # Add Notecard To Anki If Enabled
            if ANKI_UPLOAD:
                logging.info("Uploading Notecard {}...".format(word.normalized_word))
                if PARENT_DECK:
                    deck_name = LANGUAGE + "::" + str(topic).replace(" ", "_")
                else:
                    deck_name = str(topic).replace(" ", "_")
                create_note_card(card_front, card_back, tags, deck_name, DECK_TYPE)
        f.close()

if ANKI_UPLOAD:
    # Upload Media Files
    logging.info("Uploading Media...")
    logging.info("Number Of Word Files To Upload: {}".format(len(word_list)))
    count = 0
    for word in word_list:
        # Upload Audio File
        if not media_file_exists(word.audio_file):
            audio_file_path = os.path.join(os.getcwd(), "Decks\\Audio_Files\\",  word.audio_file)
            upload_media_file(word.audio_file, audio_file_path)
            if not KEEP_AUDIO:
                os.remove(audio_file_path)

        # Upload Image File
        if not media_file_exists(word.image_file):
            image_file_path = os.path.join(os.getcwd(), "Decks\\Image_Files\\",  word.image_file)
            upload_media_file(word.image_file, image_file_path)
            if not KEEP_IMAGE:
                os.remove(image_file_path)

        count += 1
        logging.info("Words Uploaded: {}".format(count))

# Syncs Anki
sync()

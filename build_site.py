#!/usr/bin/env python3
"""
Generates the Balkrishna Cards website.

Everything is generated from one place so the marketing pages, the legal pages and the
how-to-play documentation can never drift apart from the app:

  * the game rules come straight out of App/L.cs - the same strings the app shows in its
    own Rules screen, in every language we have translations for,
  * every page is a single self-contained HTML file (inline CSS, inline JS, no CDN), so it
    loads instantly on a 2G connection in a village, works offline once cached, and can be
    opened straight from the filesystem.

Run:  python3 website/build_site.py
Then: upload the whole website/ folder to balkrishnagames.in (HTTPS required - the app and
      the /join App Link both assume it).
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
APP_L = os.path.join(ROOT, "unity", "Assets", "Scripts", "App", "L.cs")

DOMAIN = "https://balkrishnagames.in"
COMPANY = "Balkrishna Enterprise"
EMAIL = "balkrishnagames@gmail.com"
APP_NAME = "Balkrishna Cards"
PLAY_URL = "https://play.google.com/store/apps/details?id=com.balkrishna.cards"

LANGS = ["en", "hi", "gu", "mr", "bn", "ta", "te", "kn", "ml", "pa", "es", "fr"]
LANG_NAMES = {
    "en": "English", "hi": "हिन्दी", "gu": "ગુજરાતી", "mr": "मराठी", "bn": "বাংলা",
    "ta": "தமிழ்", "te": "తెలుగు", "kn": "ಕನ್ನಡ", "ml": "മലയാളം", "pa": "ਪੰਜਾਬੀ",
    "es": "Español", "fr": "Français",
}
GAME_NAMES = {
    "teen_patti": "Teen Patti", "rummy": "Indian Rummy", "bluff": "Bluff",
    "andar_bahar": "Andar Bahar", "three_two_five": "3-2-5", "gulam_chor": "Gulam Chor",
    "stack": "Stack Play",
}
GAME_EMOJI = {
    "teen_patti": "♠", "rummy": "♦", "bluff": "♥",
    "andar_bahar": "♣", "three_two_five": "♠", "gulam_chor": "♥",
    "stack": "♣",
}

# ----------------------------------------------------------------------
# UI chrome, translated. Legal body text stays in English on purpose: that is
# the version both sides can rely on, and every page says so.
# ----------------------------------------------------------------------
T = {
    "en": {
        "lead": "One phone becomes the deck: seven games, up to 25 players at one table, every player in their own language.",
        "why": "What you get",
        "g1": "Seven games at launch: Teen Patti, Indian Rummy, Bluff, Andar Bahar, 3-2-5, Gulam Chor and Stack Play.",
        "g2": "Practice with bots, pass one phone around the circle, or host a private table your family joins with a code.",
        "g3": "All 25 seats play at the same time — the app deals, holds the pot and scores every hand, so nobody sits out to deal.",
        "g4": "Nearby tables keep working with no internet at all, on the same Wi-Fi or a hotspot; online tables work across cities.",
        "g5": "Each player picks their own language: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español or Français.",
        "g6": "Chips are handed out by the group leader inside the app. We never sell chips, and nothing here can be cashed out.",
        "g7": "Free to download. If you want the menus quiet, one small one-time payment removes the ads for good.",
        "g8": "No account and no phone number. Your name and your language stay on your phone.",
        "g9": "Rooms are private and reachable only by the code your group shares — no public matchmaking, no strangers.",
        "g10": "Optional avatars: pick one of twelve faces drawn by the app, or use a photo from your phone so family recognise each other at a glance.",
        "docs": "Documentation",
        "d_rules": "Word-for-word rules for every game, in twelve languages.",
        "d_terms": "What you agree to when you install and play.",
        "d_privacy": "Exactly what leaves your phone — and what never does.",
        "d_delete": "How to clear everything the app knows about you.",
        "d_support": "Hosting, joining, troubleshooting, and how to reach us.",
        "tagline": "One deck, every game — for the family table.",
        "nav_home": "Home", "nav_rules": "How to play", "nav_terms": "Terms",
        "nav_privacy": "Privacy", "nav_delete": "Delete data", "nav_support": "Support",
        "get_app": "Get it on Google Play",
        "lang_notice": "Choose your language",
        "legal_note": "This document is written in English. The summary above is a courtesy translation; "
                      "the English text is the version that governs.",
        "footer": "Made for families and friends who want to play cards without carrying a deck.",
        "rights": "All rights reserved.",
        "updated": "Last updated",
    },
    "hi": {
        "lead": "एक फ़ोन ही पूरा डेक: सात खेल, एक टेबल पर 25 खिलाड़ी तक, हर खिलाड़ी अपनी भाषा में।",
        "why": "आपको क्या मिलता है",
        "g1": "शुरुआत में सात खेल: तीन पत्ती, इंडियन रम्मी, ब्लफ़, अंदर बाहर, 3-2-5, गुलाम चोर और स्टैक प्ले।",
        "g2": "बॉट के साथ अभ्यास करें, एक फ़ोन हाथों-हाथ घुमाएँ, या अपना निजी टेबल खोलें जिसमें परिवार कोड से जुड़े।",
        "g3": "सभी 25 सीटें एक ही समय खेलती हैं — पत्ते बाँटना, गड्ढा और हर हाथ का हिसाब ऐप करता है, कोई बाँटने के लिए बैठा नहीं रहता।",
        "g4": "आसपास का टेबल बिना इंटरनेट भी चलता है — एक ही Wi-Fi या हॉटस्पॉट पर; ऑनलाइन टेबल दूसरे शहरों तक।",
        "g5": "हर खिलाड़ी अपनी भाषा चुनता है: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español या Français।",
        "g6": "चिप ग्रुप लीडर ऐप के अंदर बाँटता है। हम चिप कभी नहीं बेचते और यहाँ कुछ भी नकद नहीं हो सकता।",
        "g7": "डाउनलोड मुफ़्त। मेन्यू शांत रखने के लिए एक बार का छोटा भुगतान विज्ञापन हमेशा के लिए हटा देता है।",
        "g8": "न खाता, न फ़ोन नंबर। आपका नाम और भाषा आपके फ़ोन में ही रहते हैं।",
        "g9": "रूम निजी हैं और सिर्फ़ आपके ग्रुप के कोड से खुलते हैं — कोई सार्वजनिक मिलान नहीं, कोई अजनबी नहीं।",
        "g10": "चाहें तो अवतार चुनें: ऐप के बनाए बारह चेहरों में से एक, या अपने फ़ोन से फ़ोटो — ताकि परिवार एक-दूसरे को तुरंत पहचाने।",
        "docs": "दस्तावेज़",
        "d_rules": "हर खेल के पूरे नियम, बारह भाषाओं में।",
        "d_terms": "इंस्टॉल और खेलने पर आप क्या स्वीकार करते हैं।",
        "d_privacy": "आपके फ़ोन से क्या-क्या जाता है — और क्या कभी नहीं।",
        "d_delete": "ऐप आपके बारे में जो जानता है, वह सब कैसे हटाएँ।",
        "d_support": "टेबल बनाना, जुड़ना, समस्या हल करना, और हमसे संपर्क।",
        "tagline": "एक डेक, हर खेल — परिवार की मेज़ के लिए।",
        "nav_home": "होम", "nav_rules": "कैसे खेलें", "nav_terms": "नियम व शर्तें",
        "nav_privacy": "गोपनीयता", "nav_delete": "डेटा हटाएं", "nav_support": "सहायता",
        "get_app": "Google Play पर पाएं",
        "lang_notice": "अपनी भाषा चुनें",
        "legal_note": "यह दस्तावेज़ अंग्रेज़ी में है। ऊपर दिया सारांश सुविधा के लिए है; मान्य अंग्रेज़ी पाठ है।",
        "footer": "उन परिवारों और दोस्तों के लिए जो बिना ताश ले जाए खेलना चाहते हैं।",
        "rights": "सर्वाधिकार सुरक्षित।",
        "updated": "अंतिम अद्यतन",
    },
    "gu": {
        "lead": "એક ફોન જ પૂરું ડેક: સાત રમતો, એક ટેબલ પર 25 ખેલાડી સુધી, દરેક પોતાની ભાષામાં.",
        "why": "તમને શું મળે છે",
        "g1": "શરૂઆતમાં સાત રમતો: તીન પત્તી, ઇન્ડિયન રમી, બ્લફ, અંદર બહાર, 3-2-5, ગુલામ ચોર અને સ્ટેક પ્લે.",
        "g2": "બોટ સાથે અભ્યાસ કરો, એક ફોન હાથો-હાથ ફેરવો, અથવા પોતાનું ખાનગી ટેબલ ખોલો જેમાં પરિવાર કોડથી જોડાય.",
        "g3": "બધી 25 સીટ એક જ સમયે રમે છે — પત્તાં વહેંચવા, ગલ્લો અને દરેક હાથનો હિસાબ એપ કરે છે, કોઈ વહેંચવા બેસવું નથી.",
        "g4": "નજીકનું ટેબલ ઇન્ટરનેટ વગર પણ ચાલે છે — એક જ Wi-Fi કે હોટસ્પોટ પર; ઓનલાઇન ટેબલ શહેરો વચ્ચે.",
        "g5": "દરેક ખેલાડી પોતાની ભાષા પસંદ કરે છે: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español કે Français.",
        "g6": "ચિપ ગ્રુપ લીડર એપમાં જ આપે છે. અમે ચિપ કદી વેચતા નથી અને અહીં કંઈ પણ રોકડમાં ન થાય.",
        "g7": "ડાઉનલોડ મફત. મેનૂ શાંત રાખવા એક વારનું નાનું પેમેન્ટ જાહેરાત કાયમ માટે હટાવે છે.",
        "g8": "ના ખાતું, ના ફોન નંબર. તમારું નામ અને ભાષા તમારા ફોનમાં જ રહે છે.",
        "g9": "રૂમ ખાનગી છે અને ફક્ત તમારા ગ્રુપના કોડથી ખૂલે છે — કોઈ જાહેર મેચિંગ નહીં, કોઈ અજાણ્યા નહીં.",
        "g10": "ક્યારેય અવતાર પસંદ કરો: એપના દોરેલા બાર ચહેરામાંથી એક, અથવા તમારા ફોનમાંથી ફોટો — જેથી પરિવાર એકબીજાને તરત ઓળખે.",
        "docs": "દસ્તાવેજો",
        "d_rules": "દરેક રમતના પૂરા નિયમો, બાર ભાષાઓમાં.",
        "d_terms": "ઇન્સ્ટોલ અને રમતી વખતે તમે શું સ્વીકારો છો.",
        "d_privacy": "તમારા ફોનમાંથી શું જાય છે — અને શું કદી નહીં.",
        "d_delete": "એપ તમારા વિશે જે જાણે છે તે બધું કેમ ભૂંસવું.",
        "d_support": "ટેબલ બનાવવું, જોડાવું, સમસ્યા ઉકેલવી અને અમારો સંપર્ક.",
        "tagline": "એક ડેક, દરેક રમત — પરિવારના ટેબલ માટે.",
        "nav_home": "હોમ", "nav_rules": "કેવી રીતે રમવું", "nav_terms": "નિયમો અને શરતો",
        "nav_privacy": "ગોપનીયતા", "nav_delete": "ડેટા ડિલીટ કરો", "nav_support": "સહાય",
        "get_app": "Google Play પર મેળવો",
        "lang_notice": "તમારી ભાષા પસંદ કરો",
        "legal_note": "આ દસ્તાવેજ અંગ્રેજીમાં છે. ઉપરનો સારાંશ સમજ માટે છે; અધિકૃત અંગ્રેજી લખાણ છે.",
        "footer": "એ પરિવારો અને મિત્રો માટે જે તાશ વગર રમવા માંગે છે.",
        "rights": "સર્વ હક સ્વાધીન.",
        "updated": "છેલ્લે અપડેટ",
    },
    "mr": {
        "lead": "एक फोनच पूर्ण डेक: सात खेळ, एका टेबलावर 25 खेळाडूंपर्यंत, प्रत्येकजण आपल्या भाषेत.",
        "why": "तुम्हाला काय मिळते",
        "g1": "सुरुवातीला सात खेळ: तीन पत्ती, इंडियन रमी, ब्लफ, अंदर बाहर, 3-2-5, गुलाम चोर आणि स्टॅक प्ले.",
        "g2": "बॉटसोबत सराव करा, एक फोन हातोहात फिरवा, किंवा कुटुंब कोडने जोडणारे स्वतःचे खाजगी टेबल उघडा.",
        "g3": "सर्व 25 जागा एकाच वेळी खेळतात — पत्ते वाटणे, पात्र आणि प्रत्येक हाताचा हिशेब ॲप करते, वाटण्यासाठी कोणी बसत नाही.",
        "g4": "जवळचे टेबल इंटरनेटशिवायही चालते — एकाच Wi-Fi किंवा हॉटस्पॉटवर; ऑनलाइन टेबल शहरांपलीकडे.",
        "g5": "प्रत्येक खेळाडू स्वतःची भाषा निवडतो: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español किंवा Français.",
        "g6": "चिप्स ग्रुप लीडर ॲपमध्येच देतो. आम्ही चिप्स कधीही विकत नाही आणि इथे काहीही रोख होत नाही.",
        "g7": "डाउनलोड मोफत. मेनू शांत ठेवण्यासाठी एकदाचे छोटे पेमेंट जाहिरात कायमची हटवते.",
        "g8": "खाते नाही, फोन नंबर नाही. तुमचे नाव आणि भाषा तुमच्याच फोनमध्ये राहते.",
        "g9": "रूम खाजगी आहेत आणि फक्त तुमच्या ग्रुपच्या कोडने उघडतात — सार्वजनिक जुळवणी नाही, अनोळखी नाही.",
        "g10": "हवे असल्यास अवतार निवडा: अ‍ॅपने काढलेल्या बारा चेहऱ्यांपैकी एक, किंवा तुमच्या फोनमधून फोटो — म्हणजे कुटुंबाने एकमेकांना लगेच ओळखावे.",
        "docs": "दस्तऐवज",
        "d_rules": "प्रत्येक खेळाचे संपूर्ण नियम, बारा भाषांमध्ये.",
        "d_terms": "इन्स्टॉल करून खेळताना तुम्ही काय स्वीकारता.",
        "d_privacy": "तुमच्या फोनमधून काय जाते — आणि काय कधीच नाही.",
        "d_delete": "ॲप तुमच्याबद्दल जे जाणते ते सर्व कसे हटवायचे.",
        "d_support": "टेबल तयार करणे, जोडणे, अडचण सोडवणे आणि आमच्याशी संपर्क.",
        "tagline": "एक डेक, सर्व खेळ — कुटुंबाच्या टेबलासाठी.",
        "nav_home": "होम", "nav_rules": "कसे खेळायचे", "nav_terms": "अटी व शर्ती",
        "nav_privacy": "गोपनीयता", "nav_delete": "डेटा हटवा", "nav_support": "सहाय्य",
        "get_app": "Google Play वर मिळवा",
        "lang_notice": "तुमची भाषा निवडा",
        "legal_note": "हा दस्तऐवज इंग्रजीत आहे. वरील सारांश सुलभतेसाठी आहे; इंग्रजी मजकूर अधिकृत आहे.",
        "footer": "ज्या कुटुंबांना आणि मित्रांना पत्ते न घेता खेळायचे आहे त्यांच्यासाठी.",
        "rights": "सर्व हक्क राखीव.",
        "updated": "शेवटचे अद्यतन",
    },
    "es": {
        "lead": "Un teléfono se convierte en toda la baraja: siete juegos, hasta 25 jugadores en una mesa y cada uno en su idioma.",
        "why": "Lo que incluye",
        "g1": "Siete juegos desde el primer día: Teen Patti, Rummy indio, Bluff, Andar Bahar, 3-2-5, Gulam Chor y Stack Play.",
        "g2": "Practica con bots, pasa un solo teléfono en círculo, o abre una mesa privada a la que tu familia entra con un código.",
        "g3": "Los 25 asientos juegan a la vez: la app reparte, lleva el bote y anota cada mano, así que nadie se queda fuera repartiendo.",
        "g4": "Las mesas cercanas funcionan sin internet, en el mismo Wi-Fi o con un punto de acceso; las mesas online cruzan ciudades.",
        "g5": "Cada jugador elige su idioma: inglés, hindi, guyaratí, maratí, bengalí, tamil, telugu, canarés, malabar, panyabí, español o francés.",
        "g6": "Las fichas las reparte el líder del grupo dentro de la app. Nunca vendemos fichas y aquí nada se puede cobrar.",
        "g7": "Descarga gratuita. Si quieres los menús tranquilos, un único pago pequeño quita los anuncios para siempre.",
        "g8": "Sin cuenta y sin número de teléfono. Tu nombre y tu idioma se quedan en tu teléfono.",
        "g9": "Las salas son privadas y solo se abren con el código de tu grupo: sin emparejamiento público y sin desconocidos.",
        "g10": "Avatares opcionales: elige una de las doce caras que dibuja la app, o usa una foto de tu teléfono para que la familia se reconozca de un vistazo.",
        "docs": "Documentación",
        "d_rules": "Las reglas completas de cada juego, en doce idiomas.",
        "d_terms": "Lo que aceptas al instalar y jugar.",
        "d_privacy": "Qué sale de tu teléfono exactamente y qué no sale nunca.",
        "d_delete": "Cómo borrar todo lo que la app sabe de ti.",
        "d_support": "Crear mesa, unirse, problemas y cómo contactarnos.",
        "tagline": "Una baraja, todos los juegos, para la mesa familiar.",
        "nav_home": "Inicio", "nav_rules": "Cómo jugar", "nav_terms": "Términos",
        "nav_privacy": "Privacidad", "nav_delete": "Borrar datos", "nav_support": "Soporte",
        "get_app": "Consíguelo en Google Play",
        "lang_notice": "Elige tu idioma",
        "legal_note": "Este documento está en inglés. El resumen es una cortesía; el texto en inglés es el vigente.",
        "footer": "Hecho para familias y amigos que quieren jugar a las cartas sin llevar baraja.",
        "rights": "Todos los derechos reservados.",
        "updated": "Última actualización",
    },
    "fr": {
        "lead": "Un téléphone devient tout le jeu de cartes : sept jeux, jusqu'à 25 joueurs à la même table, chacun dans sa langue.",
        "why": "Ce que vous obtenez",
        "g1": "Sept jeux dès la sortie : Teen Patti, Rami indien, Bluff, Andar Bahar, 3-2-5, Gulam Chor et Stack Play.",
        "g2": "Entraînez-vous contre des bots, faites passer un seul téléphone, ou ouvrez une table privée où votre famille entre avec un code.",
        "g3": "Les 25 places jouent en même temps : l'appli distribue, tient le pot et compte chaque main, personne ne reste assis à distribuer.",
        "g4": "Les tables proches fonctionnent sans internet, sur le même Wi-Fi ou un partage de connexion ; les tables en ligne traversent les villes.",
        "g5": "Chaque joueur choisit sa langue : anglais, hindi, goudjarati, marathi, bengali, tamoul, télougou, kannada, malayalam, pendjabi, espagnol ou français.",
        "g6": "Les jetons sont distribués par le chef de groupe dans l'appli. Nous ne vendons jamais de jetons et rien ici ne peut être encaissé.",
        "g7": "Téléchargement gratuit. Pour des menus au calme, un seul petit paiement retire les publicités définitivement.",
        "g8": "Ni compte ni numéro de téléphone. Votre nom et votre langue restent sur votre téléphone.",
        "g9": "Les salles sont privées et ne s'ouvrent qu'avec le code de votre groupe : pas de jumelage public, pas d'inconnus.",
        "g10": "Avatars en option : l'un des douze visages dessinés par l'application, ou une photo de votre téléphone pour que la famille se reconnaisse d'un coup d'œil.",
        "docs": "Documentation",
        "d_rules": "Les règles complètes de chaque jeu, en douze langues.",
        "d_terms": "Ce que vous acceptez en installant et en jouant.",
        "d_privacy": "Ce qui quitte votre téléphone — et ce qui n'en sort jamais.",
        "d_delete": "Comment effacer tout ce que l'appli sait de vous.",
        "d_support": "Créer une table, rejoindre, dépannage et comment nous joindre.",
        "tagline": "Un jeu de cartes, tous les jeux, pour la table familiale.",
        "nav_home": "Accueil", "nav_rules": "Comment jouer", "nav_terms": "Conditions",
        "nav_privacy": "Confidentialité", "nav_delete": "Supprimer les données", "nav_support": "Aide",
        "get_app": "Disponible sur Google Play",
        "lang_notice": "Choisissez votre langue",
        "legal_note": "Ce document est rédigé en anglais. Le résumé est fourni pour votre confort ; seul le texte anglais fait foi.",
        "footer": "Conçu pour les familles et les amis qui veulent jouer sans apporter de cartes.",
        "rights": "Tous droits réservés.",
        "updated": "Dernière mise à jour",
    },
    "bn": {
        "lead": "একটি ফোনই পুরো ডেক: সাতটি খেলা, এক টেবিলে ২৫ জন পর্যন্ত, প্রত্যেকে নিজের ভাষায়।",
        "why": "আপনি কী পাবেন",
        "g1": "শুরুতেই সাতটি খেলা: তিন পত্তি, ইন্ডিয়ান রামি, ব্লাফ, আন্দর বাহার, ৩-২-৫, গোলাম চোর ও স্ট্যাক প্লে।",
        "g2": "বটের সঙ্গে অভ্যাস করুন, একটি ফোন হাতে হাতে ঘোরান, বা কোড দিয়ে পরিবার যোগ দেবে এমন ব্যক্তিগত টেবিল খুলুন।",
        "g3": "২৫টি আসনই একসঙ্গে খেলে — কার্ড বিলি, পট ও প্রতিটি হাতের হিসাব অ্যাপই করে, বিলি করতে কাউকে বসে থাকতে হয় না।",
        "g4": "কাছের টেবিল ইন্টারনেট ছাড়াও চলে — একই Wi-Fi বা হটস্পটে; অনলাইন টেবিল শহরের পর শহরে।",
        "g5": "প্রত্যেকে নিজের ভাষা বেছে নেয়: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español বা Français।",
        "g6": "চিপ গ্রুপ লিডার অ্যাপের ভিতরেই দেন। আমরা চিপ বিক্রি করি না, আর এখানে কিছুই নগদ করা যায় না।",
        "g7": "ডাউনলোড বিনামূল্যে। মেনু শান্ত রাখতে একবারের ছোট পেমেন্ট বিজ্ঞাপন চিরকালের জন্য সরায়।",
        "g8": "অ্যাকাউন্ট নেই, ফোন নম্বর নেই। আপনার নাম ও ভাষা আপনার ফোনেই থাকে।",
        "g9": "রুম ব্যক্তিগত এবং কেবল আপনার গ্রুপের কোডেই খোলে — কোনো প্রকাশ্য ম্যাচিং নেই, অপরিচিত কেউ নেই।",
        "g10": "চাইলে অবতার বাছুন: অ্যাপের আঁকা বারোটি মুখের একটি, বা আপনার ফোন থেকে ছবি — যাতে পরিবার একে অপরকে সঙ্গে সঙ্গে চিনতে পারে।",
        "docs": "নথিপত্র",
        "d_rules": "প্রতিটি খেলার পূর্ণ নিয়ম, বারোটি ভাষায়।",
        "d_terms": "ইনস্টল করে খেললে আপনি কী স্বীকার করেন।",
        "d_privacy": "আপনার ফোন থেকে কী যায় — আর কী কখনও যায় না।",
        "d_delete": "অ্যাপ আপনার সম্পর্কে যা জানে সব কীভাবে মুছবেন।",
        "d_support": "টেবিল তৈরি, যোগ দেওয়া, সমস্যা সমাধান ও আমাদের সাথে যোগাযোগ।",
        "tagline": "এক ডেক, সব খেলা — পরিবারের টেবিলের জন্য।",
        "nav_home": "হোম", "nav_rules": "কীভাবে খেলবেন", "nav_terms": "শর্তাবলি",
        "nav_privacy": "গোপনীয়তা", "nav_delete": "ডেটা মুছুন", "nav_support": "সহায়তা",
        "get_app": "Google Play-তে পান",
        "lang_notice": "আপনার ভাষা বেছে নিন",
        "legal_note": "এই নথিটি ইংরেজিতে লেখা। উপরের সারসংক্ষেপ সুবিধার জন্য; ইংরেজি পাঠই চূড়ান্ত।",
        "footer": "যে পরিবার ও বন্ধুরা তাস ছাড়াই খেলতে চান তাদের জন্য।",
        "rights": "সর্বস্বত্ব সংরক্ষিত।",
        "updated": "সর্বশেষ আপডেট",
    },
    "ta": {
        "lead": "ஒரு போனே முழு டெக்: ஏழு விளையாட்டுகள், ஒரு மேசையில் 25 பேர் வரை, ஒவ்வொருவரும் அவரவர் மொழியில்.",
        "why": "உங்களுக்கு என்ன கிடைக்கும்",
        "g1": "தொடக்கத்தில் ஏழு விளையாட்டுகள்: டீன் பட்டி, இந்தியன் ரம்மி, ப்ளஃப், அந்தர் பஹர், 3-2-5, குலாம் சோர், ஸ்டாக் ப்ளே.",
        "g2": "பாட்களுடன் பயிற்சி செய்யுங்கள், ஒரு போனை கைக்கு கை சுற்றுங்கள், அல்லது குறியீட்டால் குடும்பம் சேரும் தனிப்பட்ட மேசையைத் தொடங்குங்கள்.",
        "g3": "25 இடங்களும் ஒரே நேரத்தில் விளையாடுகின்றன — சீட்டு விநியோகம், தொகை, ஒவ்வொரு சுற்றின் கணக்கு எல்லாம் ஆப் செய்கிறது; விநியோகிக்க யாரும் உட்கார வேண்டாம்.",
        "g4": "அருகிலுள்ள மேசை இணையம் இல்லாமலும் இயங்கும் — ஒரே Wi-Fi அல்லது ஹாட்ஸ்பாட்டில்; ஆன்லைன் மேசை வேறு நகரங்களிலும்.",
        "g5": "ஒவ்வொருவரும் அவரவர் மொழியைத் தேர்ந்தெடுக்கலாம்: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español அல்லது Français.",
        "g6": "சில்லுகளை குழுத் தலைவரே ஆப்பில் வழங்குகிறார். நாங்கள் சில்லுகளை விற்கமாட்டோம்; இங்கே எதையும் பணமாக்க முடியாது.",
        "g7": "பதிவிறக்கம் இலவசம். மெனுக்கள் அமைதியாக இருக்க ஒரே முறை சிறு கட்டணம் விளம்பரங்களை நிரந்தரமாக நீக்கும்.",
        "g8": "கணக்கு இல்லை, போன் எண் இல்லை. உங்கள் பெயரும் மொழியும் உங்கள் போனிலேயே இருக்கும்.",
        "g9": "அறைகள் தனிப்பட்டவை; உங்கள் குழுவின் குறியீட்டால் மட்டுமே திறக்கும் — பொது இணைப்பு இல்லை, அந்நியர் இல்லை.",
        "g10": "விருப்பமானால் அவதாரைத் தேர்வுசெய்க: செயலி வரைந்த பன்னிரண்டு முகங்களில் ஒன்று, அல்லது உங்கள் மொபைலில் இருந்து ஒரு படம் — குடும்பத்தினர் ஒருவரை ஒருவர் உடனே அடையாளம் காண.",
        "docs": "ஆவணங்கள்",
        "d_rules": "ஒவ்வொரு விளையாட்டின் முழு விதிகளும், பன்னிரண்டு மொழிகளில்.",
        "d_terms": "நிறுவி விளையாடும்போது நீங்கள் ஒப்புக்கொள்வது.",
        "d_privacy": "உங்கள் போனை விட்டு வெளியேறுவது எது — வெளியேறாதது எது.",
        "d_delete": "ஆப் உங்களைப் பற்றி அறிந்ததை எப்படி அழிப்பது.",
        "d_support": "மேசை உருவாக்கம், இணைவது, சிக்கல் தீர்வு, எங்களை அணுகுவது.",
        "tagline": "ஒரே டெக், எல்லா விளையாட்டும் — குடும்ப மேசைக்காக.",
        "nav_home": "முகப்பு", "nav_rules": "எப்படி விளையாடுவது", "nav_terms": "விதிமுறைகள்",
        "nav_privacy": "தனியுரிமை", "nav_delete": "தரவை நீக்கு", "nav_support": "உதவி",
        "get_app": "Google Play-இல் பெறுங்கள்",
        "lang_notice": "உங்கள் மொழியைத் தேர்ந்தெடுங்கள்",
        "legal_note": "இந்த ஆவணம் ஆங்கிலத்தில் உள்ளது. மேலே உள்ள சுருக்கம் வசதிக்காக; ஆங்கில உரையே இறுதியானது.",
        "footer": "சீட்டு இல்லாமல் விளையாட விரும்பும் குடும்பங்களுக்கும் நண்பர்களுக்கும்.",
        "rights": "அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.",
        "updated": "கடைசி புதுப்பிப்பு",
    },
    "te": {
        "lead": "ఒక ఫోనే పూర్తి డెక్: ఏడు ఆటలు, ఒక టేబుల్‌పై 25 మంది వరకు, ప్రతి ఒక్కరూ తమ భాషలో.",
        "why": "మీకు ఏమి లభిస్తుంది",
        "g1": "మొదటి విడుదలలో ఏడు ఆటలు: టీన్ పట్టి, ఇండియన్ రమ్మీ, బ్లఫ్, అందర్ బహర్, 3-2-5, గులాం చోర్, స్టాక్ ప్లే.",
        "g2": "బాట్‌లతో సాధన చేయండి, ఒక ఫోన్‌ను చేతి నుంచి చేతికి అందించండి, లేదా కోడ్‌తో కుటుంబం చేరే మీ సొంత ప్రైవేట్ టేబుల్ తెరవండి.",
        "g3": "25 సీట్లు అన్నీ ఒకేసారి ఆడతాయి — పంపిణీ, పాట్, ప్రతి చేతి లెక్క యాప్ చేస్తుంది; పంపిణీకి ఎవరూ కూర్చోవాల్సిన అవసరం లేదు.",
        "g4": "దగ్గరి టేబుల్ ఇంటర్నెట్ లేకుండా కూడా నడుస్తుంది — ఒకే Wi-Fi లేదా హాట్‌స్పాట్‌లో; ఆన్‌లైన్ టేబుల్ వేరే నగరాల్లోనూ.",
        "g5": "ప్రతి ఒక్కరూ తమ భాషను ఎంచుకుంటారు: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español లేదా Français.",
        "g6": "చిప్‌లను గ్రూప్ లీడర్ యాప్‌లోనే ఇస్తారు. మేము చిప్‌లు అమ్మము, ఇక్కడ ఏదీ నగదుగా మారదు.",
        "g7": "డౌన్‌లోడ్ ఉచితం. మెనూలు ప్రశాంతంగా ఉండాలంటే ఒకసారి చిన్న చెల్లింపు ప్రకటనలను శాశ్వతంగా తొలగిస్తుంది.",
        "g8": "ఖాతా లేదు, ఫోన్ నంబర్ లేదు. మీ పేరు, భాష మీ ఫోన్‌లోనే ఉంటాయి.",
        "g9": "రూమ్‌లు ప్రైవేట్; మీ గ్రూప్ కోడ్‌తో మాత్రమే తెరుచుకుంటాయి — పబ్లిక్ మ్యాచింగ్ లేదు, అపరిచితులు లేరు.",
        "g10": "కావాలంటే అవతార్ ఎంచుకోండి: యాప్ గీసిన పన్నెండు ముఖాల్లో ఒకటి, లేదా మీ ఫోన్ నుంచి ఫోటో — కుటుంబం ఒకరినొకరు వెంటనే గుర్తించడానికి.",
        "docs": "పత్రాలు",
        "d_rules": "ప్రతి ఆట యొక్క పూర్తి నియమాలు, పన్నెండు భాషల్లో.",
        "d_terms": "ఇన్‌స్టాల్ చేసి ఆడేటప్పుడు మీరు అంగీకరించేది.",
        "d_privacy": "మీ ఫోన్ నుంచి ఏది బయటకు వెళ్తుంది — ఏది ఎప్పుడూ వెళ్లదు.",
        "d_delete": "యాప్ మీ గురించి తెలుసుకున్నదంతా ఎలా తొలగించాలి.",
        "d_support": "టేబుల్ సృష్టించడం, చేరడం, సమస్య పరిష్కారం, మమ్మల్ని సంప్రదించడం.",
        "tagline": "ఒకే డెక్, అన్ని ఆటలు — కుటుంబ బల్ల కోసం.",
        "nav_home": "హోమ్", "nav_rules": "ఎలా ఆడాలి", "nav_terms": "నిబంధనలు",
        "nav_privacy": "గోప్యత", "nav_delete": "డేటా తొలగించు", "nav_support": "సహాయం",
        "get_app": "Google Playలో పొందండి",
        "lang_notice": "మీ భాషను ఎంచుకోండి",
        "legal_note": "ఈ పత్రం ఇంగ్లీషులో ఉంది. పైన ఉన్న సారాంశం సౌలభ్యం కోసం; ఇంగ్లీషు పాఠ్యమే చెల్లుబాటు అయ్యేది.",
        "footer": "కార్డులు లేకుండా ఆడాలనుకునే కుటుంబాలు, స్నేహితుల కోసం.",
        "rights": "సర్వ హక్కులు కలవు.",
        "updated": "చివరి నవీకరణ",
    },
    "kn": {
        "lead": "ಒಂದು ಫೋನೇ ಪೂರ್ಣ ಡೆಕ್: ಏಳು ಆಟಗಳು, ಒಂದೇ ಮೇಜಿನಲ್ಲಿ 25 ಮಂದಿ ವರೆಗೆ, ಪ್ರತಿಯೊಬ್ಬರೂ ತಮ್ಮ ಭಾಷೆಯಲ್ಲಿ.",
        "why": "ನಿಮಗೆ ಏನು ಸಿಗುತ್ತದೆ",
        "g1": "ಮೊದಲ ಬಿಡುಗಡೆಯಲ್ಲಿ ಏಳು ಆಟಗಳು: ಟೀನ್ ಪಟ್ಟಿ, ಇಂಡಿಯನ್ ರಮ್ಮಿ, ಬ್ಲಫ್, ಅಂದರ್ ಬಹರ್, 3-2-5, ಗುಲಾಂ ಚೋರ್, ಸ್ಟಾಕ್ ಪ್ಲೇ.",
        "g2": "ಬಾಟ್‌ಗಳೊಂದಿಗೆ ಅಭ್ಯಾಸ ಮಾಡಿ, ಒಂದು ಫೋನ್ ಕೈಯಿಂದ ಕೈಗೆ ಹಾಕಿ, ಅಥವಾ ಕೋಡ್‌ನಿಂದ ಕುಟುಂಬ ಸೇರುವ ನಿಮ್ಮದೇ ಖಾಸಗಿ ಮೇಜು ತೆರೆಯಿರಿ.",
        "g3": "ಎಲ್ಲ 25 ಆಸನಗಳೂ ಒಟ್ಟಿಗೇ ಆಡುತ್ತವೆ — ಹಂಚಿಕೆ, ಪಾಟ್, ಪ್ರತಿ ಸುತ್ತಿನ ಲೆಕ್ಕವನ್ನು ಆ್ಯಪ್ ಮಾಡುತ್ತದೆ; ಹಂಚಲು ಯಾರೂ ಕೂರಬೇಕಿಲ್ಲ.",
        "g4": "ಹತ್ತಿರದ ಮೇಜು ಇಂಟರ್ನೆಟ್ ಇಲ್ಲದೆಯೂ ನಡೆಯುತ್ತದೆ — ಒಂದೇ Wi-Fi ಅಥವಾ ಹಾಟ್‌ಸ್ಪಾಟ್‌ನಲ್ಲಿ; ಆನ್‌ಲೈನ್ ಮೇಜು ಬೇರೆ ನಗರಗಳಲ್ಲೂ.",
        "g5": "ಪ್ರತಿಯೊಬ್ಬರೂ ತಮ್ಮ ಭಾಷೆ ಆಯ್ಕೆಮಾಡುತ್ತಾರೆ: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español ಅಥವಾ Français.",
        "g6": "ಚಿಪ್‌ಗಳನ್ನು ಗುಂಪು ನಾಯಕರೇ ಆ್ಯಪ್‌ನಲ್ಲಿ ಕೊಡುತ್ತಾರೆ. ನಾವು ಚಿಪ್ ಮಾರುವುದಿಲ್ಲ, ಇಲ್ಲಿ ಯಾವುದೂ ನಗದಾಗುವುದಿಲ್ಲ.",
        "g7": "ಡೌನ್‌ಲೋಡ್ ಉಚಿತ. ಮೆನುಗಳು ಶಾಂತವಾಗಿರಲು ಒಮ್ಮೆಯ ಸಣ್ಣ ಪಾವತಿ ಜಾಹೀರಾತನ್ನು ಶಾಶ್ವತವಾಗಿ ತೆಗೆದುಹಾಕುತ್ತದೆ.",
        "g8": "ಖಾತೆ ಇಲ್ಲ, ಫೋನ್ ಸಂಖ್ಯೆ ಇಲ್ಲ. ನಿಮ್ಮ ಹೆಸರು ಮತ್ತು ಭಾಷೆ ನಿಮ್ಮ ಫೋನ್‌ನಲ್ಲೇ ಉಳಿಯುತ್ತವೆ.",
        "g9": "ಕೊಠಡಿಗಳು ಖಾಸಗಿ; ನಿಮ್ಮ ಗುಂಪಿನ ಕೋಡ್‌ನಿಂದ ಮಾತ್ರ ತೆರೆಯುತ್ತವೆ — ಸಾರ್ವಜನಿಕ ಹೊಂದಾಣಿಕೆ ಇಲ್ಲ, ಅಪರಿಚಿತರಿಲ್ಲ.",
        "g10": "ಬೇಕಿದ್ದರೆ ಅವತಾರ್ ಆಯ್ಕೆಮಾಡಿ: ಆ್ಯಪ್ ಚಿತ್ರಿಸಿದ ಹನ್ನೆರಡು ಮುಖಗಳಲ್ಲಿ ಒಂದು, ಅಥವಾ ನಿಮ್ಮ ಫೋನ್‌ನಿಂದ ಫೋಟೋ — ಕುಟುಂಬ ಒಬ್ಬರನ್ನೊಬ್ಬರು ಕೂಡಲೇ ಗುರುತಿಸಲು.",
        "docs": "ದಾಖಲೆಗಳು",
        "d_rules": "ಪ್ರತಿ ಆಟದ ಪೂರ್ಣ ನಿಯಮಗಳು, ಹನ್ನೆರಡು ಭಾಷೆಗಳಲ್ಲಿ.",
        "d_terms": "ಇನ್‌ಸ್ಟಾಲ್ ಮಾಡಿ ಆಡುವಾಗ ನೀವು ಒಪ್ಪುವುದು.",
        "d_privacy": "ನಿಮ್ಮ ಫೋನ್‌ನಿಂದ ಏನು ಹೋಗುತ್ತದೆ — ಏನು ಎಂದಿಗೂ ಹೋಗುವುದಿಲ್ಲ.",
        "d_delete": "ಆ್ಯಪ್ ನಿಮ್ಮ ಬಗ್ಗೆ ತಿಳಿದಿರುವುದನ್ನು ಹೇಗೆ ಅಳಿಸುವುದು.",
        "d_support": "ಮೇಜು ರಚನೆ, ಸೇರುವುದು, ಸಮಸ್ಯೆ ಪರಿಹಾರ ಮತ್ತು ನಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸುವುದು.",
        "tagline": "ಒಂದೇ ಡೆಕ್, ಎಲ್ಲ ಆಟಗಳು — ಕುಟುಂಬದ ಮೇಜಿಗಾಗಿ.",
        "nav_home": "ಮುಖಪುಟ", "nav_rules": "ಹೇಗೆ ಆಡುವುದು", "nav_terms": "ನಿಯಮಗಳು",
        "nav_privacy": "ಗೌಪ್ಯತೆ", "nav_delete": "ಡೇಟಾ ಅಳಿಸಿ", "nav_support": "ಸಹಾಯ",
        "get_app": "Google Play ನಲ್ಲಿ ಪಡೆಯಿರಿ",
        "lang_notice": "ನಿಮ್ಮ ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ",
        "legal_note": "ಈ ದಾಖಲೆ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿದೆ. ಮೇಲಿನ ಸಾರಾಂಶ ಸೌಲಭ್ಯಕ್ಕಾಗಿ; ಇಂಗ್ಲಿಷ್ ಪಠ್ಯವೇ ಅಂತಿಮ.",
        "footer": "ಇಸ್ಪೀಟೆಲೆ ಇಲ್ಲದೆ ಆಡಲು ಬಯಸುವ ಕುಟುಂಬ ಮತ್ತು ಸ್ನೇಹಿತರಿಗಾಗಿ.",
        "rights": "ಎಲ್ಲಾ ಹಕ್ಕುಗಳು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ.",
        "updated": "ಕೊನೆಯ ನವೀಕರಣ",
    },
    "ml": {
        "lead": "ഒരു ഫോൺ തന്നെ മുഴുവൻ ഡെക്ക്: ഏഴ് കളികൾ, ഒരു ടേബിളിൽ 25 പേർ വരെ, ഓരോരുത്തരും സ്വന്തം ഭാഷയിൽ.",
        "why": "നിങ്ങൾക്ക് എന്ത് ലഭിക്കും",
        "g1": "ആദ്യ റിലീസിൽ ഏഴ് കളികൾ: ടീൻ പട്ടി, ഇന്ത്യൻ റമ്മി, ബ്ലഫ്, അന്തർ ബഹർ, 3-2-5, ഗുലാം ചോർ, സ്റ്റാക്ക് പ്ലേ.",
        "g2": "ബോട്ടുകളോടൊപ്പം പരിശീലിക്കുക, ഒരു ഫോൺ കൈയിൽ നിന്ന് കൈയിലേക്ക് കൈമാറുക, അല്ലെങ്കിൽ കോഡിലൂടെ കുടുംബം ചേരുന്ന സ്വന്തം സ്വകാര്യ ടേബിൾ തുറക്കുക.",
        "g3": "25 സീറ്റുകളും ഒരേ സമയം കളിക്കുന്നു — വിതരണം, പാട്ട്, ഓരോ കൈയുടെ കണക്ക് എന്നിവ ആപ്പ് ചെയ്യുന്നു; വിതരണത്തിന് ആരും ഇരിക്കേണ്ട.",
        "g4": "അടുത്തുള്ള ടേബിൾ ഇന്റർനെറ്റ് ഇല്ലാതെയും പ്രവർത്തിക്കും — ഒരേ Wi-Fi അല്ലെങ്കിൽ ഹോട്ട്സ്പോട്ടിൽ; ഓൺലൈൻ ടേബിൾ വേറെ നഗരങ്ങളിലും.",
        "g5": "ഓരോരുത്തരും സ്വന്തം ഭാഷ തിരഞ്ഞെടുക്കുന്നു: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español അല്ലെങ്കിൽ Français.",
        "g6": "ചിപ്പുകൾ ഗ്രൂപ്പ് ലീഡർ ആപ്പിൽ തന്നെ നൽകുന്നു. ഞങ്ങൾ ചിപ്പ് വിൽക്കുന്നില്ല; ഇവിടെ ഒന്നും പണമാക്കാനാവില്ല.",
        "g7": "ഡൗൺലോഡ് സൗജന്യം. മെനുകൾ ശാന്തമായിരിക്കാൻ ഒരു തവണയുള്ള ചെറിയ പേയ്മെന്റ് പരസ്യങ്ങൾ ശാശ്വതമായി നീക്കും.",
        "g8": "അക്കൗണ്ടില്ല, ഫോൺ നമ്പറില്ല. നിങ്ങളുടെ പേരും ഭാഷയും നിങ്ങളുടെ ഫോണിൽ തന്നെ നിൽക്കും.",
        "g9": "മുറികൾ സ്വകാര്യമാണ്; നിങ്ങളുടെ ഗ്രൂപ്പിന്റെ കോഡിലൂടെ മാത്രം തുറക്കും — പൊതു മാച്ചിംഗ് ഇല്ല, അപരിചിതരില്ല.",
        "g10": "വേണമെങ്കിൽ അവതാർ തിരഞ്ഞെടുക്കുക: ആപ്പ് വരച്ച പന്ത്രണ്ട് മുഖങ്ങളിൽ ഒന്ന്, അല്ലെങ്കിൽ നിങ്ങളുടെ ഫോണിൽ നിന്ന് ഒരു ഫോട്ടോ — കുടുംബം പെട്ടെന്ന് പരസ്പരം തിരിച്ചറിയാൻ.",
        "docs": "രേഖകൾ",
        "d_rules": "ഓരോ കളിയുടെയും പൂർണ്ണ നിയമങ്ങൾ, പന്ത്രണ്ട് ഭാഷകളിൽ.",
        "d_terms": "ഇൻസ്റ്റാൾ ചെയ്ത് കളിക്കുമ്പോൾ നിങ്ങൾ സമ്മതിക്കുന്നത്.",
        "d_privacy": "നിങ്ങളുടെ ഫോണിൽ നിന്ന് എന്ത് പോകുന്നു — എന്ത് ഒരിക്കലും പോകുന്നില്ല.",
        "d_delete": "ആപ്പിന് നിങ്ങളെക്കുറിച്ച് അറിയുന്നതെല്ലാം എങ്ങനെ മായ്ക്കാം.",
        "d_support": "ടേബിൾ ഉണ്ടാക്കൽ, ചേരൽ, പ്രശ്നപരിഹാരം, ഞങ്ങളെ ബന്ധപ്പെടൽ.",
        "tagline": "ഒരു ഡെക്ക്, എല്ലാ കളികളും — കുടുംബ മേശയ്ക്കായി.",
        "nav_home": "ഹോം", "nav_rules": "എങ്ങനെ കളിക്കാം", "nav_terms": "നിബന്ധനകൾ",
        "nav_privacy": "സ്വകാര്യത", "nav_delete": "വിവരങ്ങൾ മായ്ക്കുക", "nav_support": "സഹായം",
        "get_app": "Google Play-യിൽ നേടുക",
        "lang_notice": "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",
        "legal_note": "ഈ രേഖ ഇംഗ്ലീഷിലാണ്. മുകളിലെ സംഗ്രഹം സൗകര്യത്തിനുള്ളതാണ്; ഇംഗ്ലീഷ് പാഠമാണ് പ്രാബല്യത്തിലുള്ളത്.",
        "footer": "കാർഡ് കരുതാതെ കളിക്കാൻ ആഗ്രഹിക്കുന്ന കുടുംബങ്ങൾക്കും സുഹൃത്തുകൾക്കും.",
        "rights": "എല്ലാ അവകാശങ്ങളും നിക്ഷിപ്തം.",
        "updated": "അവസാന അപ്ഡേറ്റ്",
    },
    "pa": {
        "lead": "ਇੱਕ ਫੋਨ ਹੀ ਪੂਰਾ ਡੈੱਕ: ਸੱਤ ਖੇਡਾਂ, ਇੱਕ ਟੇਬਲ ’ਤੇ 25 ਖਿਡਾਰੀ ਤੱਕ, ਹਰ ਇੱਕ ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ।",
        "why": "ਤੁਹਾਨੂੰ ਕੀ ਮਿਲਦਾ ਹੈ",
        "g1": "ਪਹਿਲੀ ਰਿਲੀਜ਼ ਵਿੱਚ ਸੱਤ ਖੇਡਾਂ: ਤੀਨ ਪੱਤੀ, ਇੰਡੀਅਨ ਰੰਮੀ, ਬਲਫ, ਅੰਦਰ ਬਾਹਰ, 3-2-5, ਗੁਲਾਮ ਚੋਰ ਅਤੇ ਸਟੈਕ ਪਲੇ।",
        "g2": "ਬੋਟਾਂ ਨਾਲ ਅਭਿਆਸ ਕਰੋ, ਇੱਕ ਫੋਨ ਹੱਥੋ-ਹੱਥ ਘੁਮਾਓ, ਜਾਂ ਕੋਡ ਨਾਲ ਪਰਿਵਾਰ ਜੁੜੇ ਅਜਿਹਾ ਆਪਣਾ ਨਿੱਜੀ ਟੇਬਲ ਖੋਲ੍ਹੋ।",
        "g3": "ਸਾਰੀਆਂ 25 ਸੀਟਾਂ ਇੱਕੋ ਸਮੇਂ ਖੇਡਦੀਆਂ ਹਨ — ਪੱਤੇ ਵੰਡਣੇ, ਗੱਲ੍ਹਾ ਅਤੇ ਹਰ ਹੱਥ ਦਾ ਹਿਸਾਬ ਐਪ ਕਰਦੀ ਹੈ, ਵੰਡਣ ਲਈ ਕੋਈ ਬੈਠਦਾ ਨਹੀਂ।",
        "g4": "ਨੇੜਲਾ ਟੇਬਲ ਬਿਨਾਂ ਇੰਟਰਨੈੱਟ ਵੀ ਚੱਲਦਾ ਹੈ — ਇੱਕੋ Wi-Fi ਜਾਂ ਹਾਟਸਪਾਟ ’ਤੇ; ਆਨਲਾਈਨ ਟੇਬਲ ਹੋਰ ਸ਼ਹਿਰਾਂ ਵਿੱਚ ਵੀ।",
        "g5": "ਹਰ ਖਿਡਾਰੀ ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣਦਾ ਹੈ: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español ਜਾਂ Français।",
        "g6": "ਚਿੱਪਾਂ ਗਰੁੱਪ ਲੀਡਰ ਐਪ ਵਿੱਚ ਹੀ ਦਿੰਦਾ ਹੈ। ਅਸੀਂ ਚਿੱਪਾਂ ਕਦੇ ਨਹੀਂ ਵੇਚਦੇ ਅਤੇ ਇੱਥੇ ਕੁਝ ਵੀ ਨਕਦ ਨਹੀਂ ਹੁੰਦਾ।",
        "g7": "ਡਾਊਨਲੋਡ ਮੁਫ਼ਤ। ਮੀਨੂੰ ਸ਼ਾਂਤ ਰੱਖਣ ਲਈ ਇੱਕ ਵਾਰ ਦਾ ਛੋਟਾ ਭੁਗਤਾਨ ਇਸ਼ਤਿਹਾਰ ਹਮੇਸ਼ਾ ਲਈ ਹਟਾ ਦਿੰਦਾ ਹੈ।",
        "g8": "ਨਾ ਖਾਤਾ, ਨਾ ਫੋਨ ਨੰਬਰ। ਤੁਹਾਡਾ ਨਾਮ ਤੇ ਭਾਸ਼ਾ ਤੁਹਾਡੇ ਫੋਨ ਵਿੱਚ ਹੀ ਰਹਿੰਦੇ ਹਨ।",
        "g9": "ਰੂਮ ਨਿੱਜੀ ਹਨ ਅਤੇ ਸਿਰਫ਼ ਤੁਹਾਡੇ ਗਰੁੱਪ ਦੇ ਕੋਡ ਨਾਲ ਖੁੱਲ੍ਹਦੇ ਹਨ — ਕੋਈ ਜਨਤਕ ਮਿਲਾਨ ਨਹੀਂ, ਕੋਈ ਅਣਜਾਣ ਨਹੀਂ।",
        "g10": "ਚਾਹੋ ਤਾਂ ਅਵਤਾਰ ਚੁਣੋ: ਐਪ ਦੇ ਬਣਾਏ ਬਾਰਾਂ ਚਿਹਰਿਆਂ ਵਿੱਚੋਂ ਇੱਕ, ਜਾਂ ਤੁਹਾਡੇ ਫ਼ੋਨ ਤੋਂ ਫ਼ੋਟੋ — ਤਾਂ ਜੋ ਪਰਿਵਾਰ ਇੱਕ-ਦੂਜੇ ਨੂੰ ਤੁਰੰਤ ਪਛਾਣੇ।",
        "docs": "ਦਸਤਾਵੇਜ਼",
        "d_rules": "ਹਰ ਖੇਡ ਦੇ ਪੂਰੇ ਨਿਯਮ, ਬਾਰਾਂ ਭਾਸ਼ਾਵਾਂ ਵਿੱਚ।",
        "d_terms": "ਇੰਸਟਾਲ ਕਰਕੇ ਖੇਡਣ ਵੇਲੇ ਤੁਸੀਂ ਕੀ ਮੰਨਦੇ ਹੋ।",
        "d_privacy": "ਤੁਹਾਡੇ ਫੋਨ ਤੋਂ ਕੀ ਜਾਂਦਾ ਹੈ — ਅਤੇ ਕੀ ਕਦੇ ਨਹੀਂ।",
        "d_delete": "ਐਪ ਤੁਹਾਡੇ ਬਾਰੇ ਜੋ ਜਾਣਦੀ ਹੈ ਉਹ ਸਭ ਕਿਵੇਂ ਮਿਟਾਉਣਾ।",
        "d_support": "ਟੇਬਲ ਬਣਾਉਣਾ, ਜੁੜਨਾ, ਸਮੱਸਿਆ ਹੱਲ ਤੇ ਸਾਡੇ ਨਾਲ ਸੰਪਰਕ।",
        "tagline": "ਇੱਕ ਡੈੱਕ, ਹਰ ਖੇਡ — ਪਰਿਵਾਰ ਦੇ ਮੇਜ਼ ਲਈ।",
        "nav_home": "ਘਰ", "nav_rules": "ਕਿਵੇਂ ਖੇਡਣਾ ਹੈ", "nav_terms": "ਨਿਯਮ ਤੇ ਸ਼ਰਤਾਂ",
        "nav_privacy": "ਪਰਦੇਦਾਰੀ", "nav_delete": "ਡਾਟਾ ਮਿਟਾਓ", "nav_support": "ਸਹਾਇਤਾ",
        "get_app": "Google Play 'ਤੇ ਲਵੋ",
        "lang_notice": "ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ",
        "legal_note": "ਇਹ ਦਸਤਾਵੇਜ਼ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਹੈ। ਉੱਪਰ ਦਿੱਤਾ ਸਾਰ ਸਹੂਲਤ ਲਈ ਹੈ; ਅੰਗਰੇਜ਼ੀ ਪਾਠ ਹੀ ਮੰਨਿਆ ਜਾਵੇਗਾ।",
        "footer": "ਉਹਨਾਂ ਪਰਿਵਾਰਾਂ ਤੇ ਦੋਸਤਾਂ ਲਈ ਜੋ ਬਿਨਾਂ ਤਾਸ਼ ਲਿਜਾਏ ਖੇਡਣਾ ਚਾਹੁੰਦੇ ਹਨ।",
        "rights": "ਸਾਰੇ ਹੱਕ ਰਾਖਵੇਂ।",
        "updated": "ਆਖਰੀ ਅੱਪਡੇਟ",
    },
}

CSS = """
:root{--felt:#0B3D2E;--felt2:#12523E;--gold:#E7B44C;--cream:#F7F2E7;--ink:#1A1A1F;--soft:#22262b;--danger:#C0392B;--good:#2E9E5B}
*{box-sizing:border-box}
body{margin:0;background:linear-gradient(180deg,var(--felt) 0%,#08281e 100%);color:var(--cream);
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans","Noto Sans Devanagari",Arial,sans-serif;
 line-height:1.65;-webkit-text-size-adjust:100%}
a{color:var(--gold)}
header{position:sticky;top:0;background:rgba(8,40,30,.96);border-bottom:1px solid rgba(231,180,76,.35);padding:10px 16px;z-index:5}
.wrap{max-width:900px;margin:0 auto;padding:20px 16px 60px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:20px;color:var(--gold);text-decoration:none}
nav a{display:inline-block;padding:6px 10px;border-radius:8px;text-decoration:none;font-size:15px}
nav a:hover{background:rgba(231,180,76,.15)}
h1{font-size:30px;line-height:1.25;margin:24px 0 8px;color:var(--gold)}
h2{font-size:22px;margin:28px 0 8px;color:var(--gold)}
h3{font-size:18px;margin:20px 0 6px}
p,li{font-size:17px}
.tag{color:#cfe9dd;font-size:18px;margin:0 0 20px}
.card{background:rgba(255,255,255,.06);border:1px solid rgba(231,180,76,.25);border-radius:14px;padding:16px 18px;margin:14px 0}
.btn{display:inline-block;background:var(--good);color:#06251a;font-weight:700;padding:12px 18px;border-radius:10px;
 text-decoration:none;margin:8px 8px 8px 0}
.btn.alt{background:var(--gold);color:#2a1d00}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
.pill{display:inline-block;background:rgba(231,180,76,.14);border:1px solid rgba(231,180,76,.35);
 border-radius:999px;padding:4px 12px;margin:3px 4px 3px 0;font-size:14px;cursor:pointer}
.pill.on{background:var(--gold);color:#2a1d00;font-weight:700}
.rules li{margin:6px 0}
footer{border-top:1px solid rgba(231,180,76,.25);padding:20px 16px 40px;color:#bcd6c9;font-size:14px}
.small{font-size:14px;color:#bcd6c9}
table{width:100%;border-collapse:collapse;font-size:16px}
td,th{border-bottom:1px solid rgba(255,255,255,.12);padding:8px 6px;text-align:left}
.notice{background:rgba(46,158,91,.16);border-left:4px solid var(--good);padding:10px 14px;border-radius:8px}
.warn{background:rgba(192,57,43,.14);border-left:4px solid var(--danger);padding:10px 14px;border-radius:8px}
"""

JS_CHROME = """
// Language switching. The choice is remembered so a returning visitor lands in their language.
(function () {
  var T = %s;
  var KEY = 'bk_lang';
  function pick() {
    var q = new URLSearchParams(location.search).get('lang');
    if (q && T[q]) return q;
    var saved = localStorage.getItem(KEY);
    if (saved && T[saved]) return saved;
    var nav = (navigator.language || 'en').slice(0, 2);
    return T[nav] ? nav : 'en';
  }
  function apply(code) {
    var dict = T[code] || T.en;
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var k = el.getAttribute('data-i18n');
      if (dict[k]) el.textContent = dict[k];
    });
    document.documentElement.lang = code;
    document.querySelectorAll('.langpick').forEach(function (el) {
      el.className = 'pill langpick' + (el.getAttribute('data-lang') === code ? ' on' : '');
    });
    localStorage.setItem(KEY, code);
  }
  window.bkSetLang = function (code) { apply(code); if (window.onLangChange) window.onLangChange(code); };
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.langpick').forEach(function (el) {
      el.addEventListener('click', function () { window.bkSetLang(el.getAttribute('data-lang')); });
    });
    apply(pick());
  });
})();
"""


def chrome(code):
    """Header + footer shared by every page, language-agnostic markup."""
    links = "".join(
        f'<a href="{href}" data-i18n="{key}">{T["en"][key]}</a>'
        for href, key in [("index.html", "nav_home"), ("rules.html", "nav_rules"),
                          ("terms.html", "nav_terms"), ("privacy.html", "nav_privacy"),
                          ("delete-account.html", "nav_delete"), ("support.html", "nav_support")]
    )
    return f"""<header><div class="wrap" style="padding:0">
<a class="brand" href="index.html">♠ {APP_NAME}</a>
<nav style="margin-top:6px">{links}</nav>
</div></header>"""


def footer(code, updated):
    t = T["en"]
    return f"""<footer><div class="wrap">
<p><strong>{APP_NAME}</strong> — {t['footer']}</p>
<p>{COMPANY} · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{DOMAIN}">{DOMAIN}</a></p>
<p class="small">© {year()} {COMPANY}. {t['rights']} · {t['updated']}: {updated}</p>
</div></footer>"""


def year():
    import datetime
    return datetime.date.today().year


def lang_bar():
    pills = "".join(
        f'<span class="pill langpick" data-lang="{c}">{LANG_NAMES[c]}</span>' for c in
        ["en", "hi", "gu", "mr", "bn", "ta", "te", "kn", "ml", "pa", "es", "fr"]
    )
    return f'<div class="card"><p class="small" data-i18n="lang_notice">Choose your language</p>{pills}</div>'


def page(title, body, lang_data=True, updated="14 September 2026"):
    chrome_js = JS_CHROME % json.dumps(T, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {APP_NAME}</title>
<meta name="description" content="{APP_NAME} — play Teen Patti, Rummy, Bluff, Andar Bahar, 3-2-5 and Gulam Chor with your family and friends. One deck, every game, no real money.">
<style>{CSS}</style>
</head>
<body>
{chrome('en')}
<div class="wrap">
{body}
</div>
{footer('en', updated)}
<script>{chrome_js}</script>
</body>
</html>
"""


# ----------------------------------------------------------------------
def read_rules():
    src = open(APP_L, encoding="utf-8").read()
    block = re.search(r"private static Dictionary<string, string\[\]> BuildRules\(\).*?return d;\s*\}", src, re.S).group(0)
    data = {}
    for m in re.finditer(r'add\("rules\.([a-z_]+)",\s*new string\[\]\s*\{(.*?)\}\);', block, re.S):
        gid, body = m.group(1), m.group(2)
        items, cur, inq, esc = [], "", False, False
        for ch in body:
            if esc: cur += ch; esc = False; continue
            if ch == "\\": cur += ch; esc = True; continue
            if ch == '"': inq = not inq; cur += ch; continue
            if ch == "," and not inq: items.append(cur.strip()); cur = ""
            else: cur += ch
        if cur.strip(): items.append(cur.strip())
        vals = []
        for it in items:
            it = it.strip()
            if it.startswith('"') and it.endswith('"'): it = it[1:-1]
            try: vals.append(json.loads('"' + it + '"'))
            except Exception: vals.append(it)
        per_lang = {}
        for i, code in enumerate(LANGS):
            text = vals[i] if i < len(vals) and vals[i] else (vals[0] if vals else "")
            per_lang[code] = [p.strip() for p in text.split("|") if p.strip()]
        data[gid] = per_lang
    return data


def build():
    rules = read_rules()
    written = []

    # ---------------- index ----------------
    index = f"""
<h1 data-i18n="app_head">{APP_NAME}</h1>
<p class="tag" data-i18n="tagline">One deck, every game — for the family table.</p>
{lang_bar()}
<div class="card">
<p class="tag" data-i18n="lead">One phone becomes the deck: seven games, up to 25 players at one table, every player in their own language.</p>
<h3 data-i18n="why">What you get</h3>
<ul>
<li data-i18n="g1">Seven games at launch: Teen Patti, Indian Rummy, Bluff, Andar Bahar, 3-2-5, Gulam Chor and Stack Play.</li>
<li data-i18n="g2">Practice with bots, pass one phone around the circle, or host a private table your family joins with a code.</li>
<li data-i18n="g3">All 25 seats play at the same time — the app deals, holds the pot and scores every hand, so nobody sits out to deal.</li>
<li data-i18n="g4">Nearby tables keep working with no internet at all, on the same Wi-Fi or a hotspot; online tables work across cities.</li>
<li data-i18n="g5">Each player picks their own language: English, हिन्दी, ગુજરાતી, मराठी, বাংলা, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ਪੰਜਾਬੀ, Español or Français.</li>
<li data-i18n="g6">Chips are handed out by the group leader inside the app. We never sell chips, and nothing here can be cashed out.</li>
<li data-i18n="g7">Free to download. If you want the menus quiet, one small one-time payment removes the ads for good.</li>
<li data-i18n="g8">No account and no phone number. Your name and your language stay on your phone.</li>
<li data-i18n="g9">Rooms are private and reachable only by the code your group shares — no public matchmaking, no strangers.</li>
<li data-i18n="g10">Optional avatars: pick one of twelve faces drawn by the app, or use a photo from your phone so family recognise each other at a glance.</li>
</ul>
<a class="btn" href="{PLAY_URL}" data-i18n="get_app">Get it on Google Play</a>
<a class="btn alt" href="rules.html" data-i18n="nav_rules">How to play</a>
</div>

<h2 data-i18n="docs">Documentation</h2>
<div class="card">
<p><a href="rules.html" data-i18n="nav_rules">How to play</a> — <span data-i18n="d_rules">Word-for-word rules for every game, in twelve languages.</span></p>
<p><a href="terms.html" data-i18n="nav_terms">Terms</a> — <span data-i18n="d_terms">What you agree to when you install and play.</span></p>
<p><a href="privacy.html" data-i18n="nav_privacy">Privacy</a> — <span data-i18n="d_privacy">Exactly what leaves your phone — and what never does.</span></p>
<p><a href="delete-account.html" data-i18n="nav_delete">Delete data</a> — <span data-i18n="d_delete">How to clear everything the app knows about you.</span></p>
<p><a href="support.html" data-i18n="nav_support">Support</a> — <span data-i18n="d_support">Hosting, joining, troubleshooting, and how to reach us.</span></p>
</div>
"""
    write("index.html", page(APP_NAME, index))
    written.append("index.html")

    # ---------------- rules ----------------
    rules_json = json.dumps({"names": GAME_NAMES, "emoji": GAME_EMOJI, "rules": rules}, ensure_ascii=False)
    body = f"""
<h1>How to play</h1>
<p class="tag">Every game, fully documented — in twelve languages. These are the same rules the app
shows in its help screen, so a table can never argue about a house rule.</p>
{lang_bar()}
<div id="gameSwitch" class="card"></div>
<div id="ruleBox" class="card rules"></div>
<p class="small">Translations for Bangla, Tamil, Telugu, Kannada, Malayalam and Punjabi are being
filled in game by game; until a translation is complete the page shows the English rules rather
than a machine translation, because a wrong rule is worse than an English one.</p>
<script>
var BK_RULES = {rules_json};
(function () {{
  var langs = {json.dumps(LANGS)};
  var langNames = {json.dumps(LANG_NAMES, ensure_ascii=False)};
  var order = {json.dumps(list(rules.keys()))};
  var current = 'en', game = order[0];

  function render() {{
    var sw = document.getElementById('gameSwitch'), box = document.getElementById('ruleBox');
    sw.innerHTML = order.map(function (g) {{
      return '<span class="pill' + (g === game ? ' on' : '') + '" data-g="' + g + '">' +
             BK_RULES.emoji[g] + ' ' + BK_RULES.names[g] + '</span>';
    }}).join(' ');
    var lines = (BK_RULES.rules[game] || {{}})['en'] || [];
    var lines2 = (BK_RULES.rules[game] || {{}})[current] || lines;
    var isFallback = !((BK_RULES.rules[game] || {{}})[current] || []).length;
    box.innerHTML = '<h2>' + BK_RULES.names[game] + '</h2><ol>' +
      lines2.map(function (l) {{ return '<li>' + l + '</li>'; }}).join('') + '</ol>' +
      (isFallback && current !== 'en' ? '<p class="small">Showing English rules for ' +
        langNames[current] + '.</p>' : '');
    sw.querySelectorAll('[data-g]').forEach(function (el) {{
      el.addEventListener('click', function () {{ game = el.getAttribute('data-g'); render(); }});
    }});
  }}
  window.onLangChange = function (code) {{ current = code; render(); }};
  document.addEventListener('DOMContentLoaded', function () {{
    current = localStorage.getItem('bk_lang') || 'en';
    render();
  }});
}})();
</script>
"""
    write("rules.html", page("How to play", body))
    written.append("rules.html")

    # ---------------- terms ----------------
    terms = f"""
<h1>Terms &amp; Conditions</h1>
<p class="tag">Effective {year()}-09-14 · {COMPANY}</p>
{lang_bar()}
<div class="card">
<p><strong>In short:</strong> Balkrishna Cards is a free card-game app for private groups of
family and friends. There is no real-money play, no wagering, no prizes and no cash-out. Chips are
virtual, worth nothing, and are handed out by the group leader inside the app. You must be at least
13 years old. Play nicely.</p>
<p class="small" data-i18n="legal_note"></p>
</div>

<h2>1. Who we are</h2>
<p>{APP_NAME} is published by {COMPANY} ("we", "us"). You can reach us at
<a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

<h2>2. Accepting these terms</h2>
<p>By installing or using the app you agree to these Terms and to our
<a href="privacy.html">Privacy Policy</a>. If you do not agree, please do not use the app. You may
open the app to read these documents without agreeing; the app remains usable, and you can agree
later from Settings.</p>

<h2>3. Virtual chips only — no gambling</h2>
<ul>
<li>Chips in {APP_NAME} are a game counter. They have <strong>no monetary value</strong>, cannot be
bought, sold, transferred outside a table, exchanged for cash or prizes, or redeemed in any way.</li>
<li>We do not operate, host, or facilitate wagering. The app is a card-game table, not a betting
service.</li>
<li>Chips are allocated by the leader of a group inside the app, purely to keep the game moving.
We never sell chips and never award chips for a payment.</li>
<li>Any advertisement shown is a normal advertising placement, not a stake.</li>
</ul>

<h2>4. Eligibility</h2>
<p>You must be at least 13 years old to use {APP_NAME}. If you are under 18, please play with the
knowledge of a parent or guardian. The app is rated for teen audiences on Google Play and does not
present real-money gambling.</p>

<h2>5. Your responsibilities</h2>
<ul>
<li>Use your real first name or a nickname — no impersonating other people.</li>
<li>Your avatar is yours to choose, and yours to answer for: choose a built-in face, or use a photo
you have the right to share with the people at your table. Do not use someone else's picture, and do
not use a picture that would be offensive or unlawful. See the
<a href="privacy.html">Privacy Policy</a>, section 3, for what happens to a picture you pick.</li>
<li>Do not use the app to harass, threaten, or defraud anyone, and do not use it for any unlawful
purpose, including any form of real-money betting between players.</li>
<li>Do not attempt to reverse engineer, decompile, tamper with, or disrupt the app or the relay
service, or use modified clients to gain an advantage at a table.</li>
<li>You are responsible for what your device does on the network you connect it to.</li>
</ul>

<h2>6. Private groups and room codes</h2>
<p>Tables are joined with a short code shared by the group leader. There is no public matchmaking
and no way to browse for strangers' tables. Codes expire automatically, and rooms are deleted six
hours after their last activity. Do not share a code publicly if you do not want others to join.</p>

<h2>7. Availability and changes</h2>
<p>Online play depends on a relay service we run. We may change, suspend, or discontinue any part of
the app or the service, including individual games, and may release updates that change how games
behave. We aim to keep offline play always available.</p>

<h2>8. Intellectual property</h2>
<p>The app, its artwork, its code, and its documentation belong to {COMPANY}. The card games
themselves are traditional public-domain games; our implementation is not. You receive a personal,
non-exclusive, non-transferable licence to use the app on your own devices.</p>

<h2>9. Advertising and the one purchase</h2>
<p>The free version may show ads, on the menus only and never while a hand is being played. Ad
selection and data handling for ads is described in our Privacy Policy, and the ad network's own
policies apply to the ad content.</p>
<p>The only thing that can be bought in {APP_NAME} is a one-time purchase that removes those ads. It
grants nothing else: no chips, no advantage at any table, nothing that can be cashed out. The
purchase is handled entirely by Google Play, and we never see your payment details.</p>

<h2>10. Disclaimer and liability</h2>
<p>The app is provided "as is" without warranties of any kind. To the maximum extent permitted by
law, {COMPANY} is not liable for indirect or consequential losses arising from use of the app,
including lost games, lost virtual chips, or interrupted play. Nothing in these terms limits
liability that cannot be limited by law.</p>

<h2>11. Termination</h2>
<p>You may stop using the app at any time and delete your data as described on the
<a href="delete-account.html">delete data page</a>. We may restrict access if the app is misused.</p>

<h2>12. Governing law</h2>
<p>These terms are governed by the laws of India, and the courts of Gujarat, India have exclusive
jurisdiction over any dispute.</p>

<h2>13. Changes to these terms</h2>
<p>We will update the date at the top of this page when these terms change. Continuing to use the
app after a change means you accept the new terms.</p>
"""
    write("terms.html", page("Terms & Conditions", terms))
    written.append("terms.html")

    # ---------------- privacy ----------------
    privacy = f"""
<h1>Privacy Policy</h1>
<p class="tag">Effective {year()}-09-14 · {COMPANY}</p>
{lang_bar()}
<div class="card">
<p><strong>In short:</strong> there is no account and no login. The app stores your name, language
and preferences on your own phone. When you play online, your display name, your avatar and your
moves travel through our relay so the other players can see them. Ads and crash reporting are
handled by Google. We do not sell your data; we do not collect your phone number, contacts or
location; and we never read your photo library — the picture you may choose as an avatar is
optional, is opened through Android's own file chooser, and is shown only to the people at your
table.</p>
<p class="small" data-i18n="legal_note"></p>
</div>

<h2>1. What the app stores on your phone</h2>
<table>
<tr><th>Data</th><th>Why</th></tr>
<tr><td>Your name (whatever you type)</td><td>So other players at your table know who you are</td></tr>
<tr><td>Language, sound, notification preferences</td><td>So the app speaks your language and behaves as you set it</td></tr>
<tr><td>Consent state and date</td><td>To show the Terms &amp; Conditions notice only once</td></tr>
<tr><td>Games played, review prompt state</td><td>To ask for a Play Store rating at a sensible moment and not more often</td></tr>
<tr><td>Chips and starting stack for a table</td><td>Game state only — these are virtual and have no value</td></tr>
<tr><td>Your avatar: a built-in face, or a picture you chose</td><td>So other players recognise you. A chosen picture is shrunk to 96×96 and stored in the app's own folder on this phone; "Remove my photo" deletes it</td></tr>
</table>
<p>All of it lives in the app's private storage on your device. Uninstalling the app removes it.</p>

<h2>2. What leaves your phone</h2>
<ul>
<li><strong>Online play (optional).</strong> If you host or join an internet room, the relay receives
your display name, a room code, and every move made at that table (for example "seat 2 played a
card"). It does not receive your cards, your phone number, or your contacts. Move logs are kept in
memory only and deleted with the room, six hours after the last activity.</li>
<li><strong>Nothing at all for offline play.</strong> Practice games and pass-and-play never touch
the network.</li>
<li><strong>Nearby play.</strong> Travels directly between the phones on your Wi-Fi or hotspot. It
does not reach the internet.</li>
<li><strong>Your avatar.</strong> Only in an online room of twelve players or fewer, your avatar —
the picture, if you chose one — travels with your display name so the table can recognise you. It is
never used for advertising and is not kept beyond the room. Section 3 explains exactly what that
means for a photo.</li>
</ul>

<h2>3. Avatars and photos (optional, and yours to control)</h2>
<ul>
<li><strong>What you can choose.</strong> One of twelve faces the app draws itself, or — if you tap
"Use a photo from my phone" — a picture from your device.</li>
<li><strong>No album access.</strong> The picker is Android's own file chooser. It hands the app the
one picture you tapped and nothing else: the app cannot list or read anything else in your gallery,
and it asks for no storage or photo permission at all. There is no such permission in the app's
manifest.</li>
<li><strong>What happens to a picture you pick.</strong> The middle square is cut out, shrunk to
96×96, saved in the app's own private folder on your phone, and nowhere else. "Remove my photo" in
the avatar sheet deletes it; clearing the app's data or uninstalling removes it too.</li>
<li><strong>When it is shared, and with whom.</strong> In an online room of twelve players or fewer,
the picture travels through our relay to the other players at that table, so they see your face
beside your name. That is the only thing it is ever used for: never advertising, never analytics,
never shared with anyone outside that room. It lives in memory with the room, and rooms are deleted
no later than six hours after the last activity. In a room of more than twelve players, and in
nearby or offline play, no picture is sent at all — only a built-in face travels.</li>
<li><strong>Other players' pictures.</strong> Another player's avatar is theirs. Do not copy or use
a picture you have no right to share.</li>
</ul>

<h2>4. Advertising</h2>
<p>The free version uses Google AdMob. AdMob may collect a device advertising identifier and
approximate, coarse information to select and measure ads. You can limit ad personalisation in your
Android settings (Settings → Privacy → Ads). Where consent is required by law, the ad SDK requests
it. Choosing to remove ads (when offered) is a purchase handled entirely by Google Play; we never
see your payment details.</p>

<h2>5. Crash reports and diagnostics</h2>
<p>If crash reporting is enabled in a release, Google Play collects anonymous crash and ANR reports
to help us fix bugs. These contain a stack trace and device model, not your personal data. The build
ships native debug symbols precisely so these reports are useful without collecting anything extra
from you.</p>

<h2>6. Children</h2>
<p>The app is not directed to children under 13. We do not knowingly collect personal information
from children under 13. If you believe a child has provided information, write to us and we will
delete it.</p>

<h2>7. Your rights</h2>
<p>Because we hold almost nothing, your rights are mostly exercised on your device: clear the app's
data or uninstall it to erase everything it stored. For anything held by our relay (for example a
move log that has not yet expired) or by our service providers, email
<a href="mailto:{EMAIL}">{EMAIL}</a> and we will delete it. See the
<a href="delete-account.html">delete data page</a> for the exact steps, which is also the process
Google Play requires us to publish.</p>

<h2>8. Security and retention</h2>
<p>Online rooms are ephemeral: a code, a seed and an ordered list of moves, kept in memory and
deleted no later than six hours after the last activity. We use HTTPS for all traffic to the relay.
No method of transmission is perfectly secure, so please do not treat the app as a place for
sensitive information — it is a card table.</p>

<h2>9. International users</h2>
<p>Our relay and our providers may process data in countries other than yours, including India and
the United States. By using online play you consent to that transfer.</p>

<h2>10. Changes</h2>
<p>If this policy changes, the date at the top changes with it. Material changes will also be
noted in the app's Play Store listing.</p>

<h2>11. Contact</h2>
<p>{COMPANY}<br>Email: <a href="mailto:{EMAIL}">{EMAIL}</a><br>Website: <a href="{DOMAIN}">{DOMAIN}</a></p>
"""
    write("privacy.html", page("Privacy Policy", privacy))
    written.append("privacy.html")

    # ---------------- delete account ----------------
    delete = f"""
<h1>Delete your account and data</h1>
<p class="tag">Google Play requires every app to explain this. Here is exactly how it works in
{APP_NAME}.</p>
{lang_bar()}
<div class="card">
<p class="notice"><strong>The short version:</strong> there is no account to delete — {APP_NAME}
has no login. Everything the app knows about you is stored on your own phone and disappears when
you clear the app's data or uninstall it. If you have played online and want the temporary
room data erased sooner, email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div>

<h2>Method 1 — Clear the data yourself, instantly</h2>
<ol>
<li>Open {APP_NAME}.</li>
<li>Tap <strong>Settings</strong> on the home screen.</li>
<li>Tap <strong>Delete my data (this phone)</strong>, then confirm <strong>Delete</strong>.</li>
</ol>
<p>This erases your name, language, sound and notification preferences, consent record, chip
settings, review-prompt state and your avatar — including a picture you chose — from this device
immediately, and returns the app to its first-run state.</p>

<h2>Method 2 — Uninstall</h2>
<p>Uninstalling the app removes its private storage, and with it every piece of data listed above.</p>

<h2>Method 3 — Ask us to delete server-side data</h2>
<p>Online rooms hold only a room code, a display name and the list of moves, kept in memory and
deleted automatically within six hours of the table going quiet. If you want that removed sooner,
or you have written to support before and want our correspondence deleted:</p>
<ol>
<li>Email <a href="mailto:{EMAIL}?subject=Delete%20my%20data">{EMAIL}</a> with the subject
"Delete my data".</li>
<li>Include the name you used in the app and, if you have it, the room code (it looks like
<code>7KQ4ZM</code>). If you do not have the code, the date and time of the game is enough.</li>
<li>We reply within 30 days confirming deletion. Because we hold no account, there is no partial
state to keep.</li>
</ol>

<h2>What is deleted, and what is kept</h2>
<table>
<tr><th>Data</th><th>What happens</th></tr>
<tr><td>Name, language, preferences, consent record</td><td>Deleted from your phone when you clear the data or uninstall</td></tr>
<tr><td>Your avatar — a built-in face, or a picture you chose</td><td>Both live in the app's own folder on this phone and go with the same action. A chosen picture can also be removed on its own with "Remove my photo" in the avatar sheet</td></tr>
<tr><td>Avatars shown at an online table</td><td>Held in memory with the room and deleted with it (within six hours); a picture is only ever sent for tables of twelve or fewer players</td></tr>
<tr><td>Virtual chips and table settings</td><td>Deleted with the same action; they have no value and cannot be restored</td></tr>
<tr><td>Room codes and move logs (online play)</td><td>Deleted automatically within six hours; on request we delete them immediately</td></tr>
<tr><td>Crash reports held by Google Play</td><td>Anonymous and retained per Google's policy; we cannot link them to you</td></tr>
<tr><td>Ad identifiers held by the ad network</td><td>Controlled by your Android privacy settings; reset or limit them there</td></tr>
</table>

<h2>Contact</h2>
<p>{COMPANY}<br>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
"""
    write("delete-account.html", page("Delete your data", delete))
    written.append("delete-account.html")

    # ---------------- support ----------------
    support = f"""
<h1>Support</h1>
<p class="tag">Stuck at a table? These are the things that actually come up.</p>
{lang_bar()}

<h2>Starting a table</h2>
<p>The group leader: tap <strong>Host a table</strong> on the home screen, then share the room code
with the family — the invite button opens WhatsApp with a message and a link already written. When
everyone is in the lobby, the leader taps <strong>Deal the cards</strong>. Nearby tables work with
no internet (same Wi-Fi or one phone's hotspot); online tables work across cities.</p>

<h2>Joining a table</h2>
<p>Tap <strong>Join with a code</strong>, type the six characters the leader sent you, and take your
seat. Codes exclude characters like 0 and O that get misread when read aloud. If a code is refused,
the room has probably expired — rooms close six hours after the last activity.</p>

<h2>Where do chips come from?</h2>
<p>From the group leader. Chips in Balkrishna Cards are virtual, are never sold, and can never be
cashed out or converted into anything. There is no way to buy chips, and no in-app purchase that
gives an advantage.</p>

<h2>The game says a move is not allowed</h2>
<p>The app only shows moves the rules permit, and it checks every move again before accepting it. If
a button does nothing, the usual causes are: it is not your turn, you are showing a packed hand, or
a card you selected was already discarded. Rejected moves always explain themselves in a small
message at the bottom of the screen.</p>

<h2>My cards went to the wrong player in pass-and-play</h2>
<p>Pass-and-play shows one hand at a time: the phone should be passed after each turn. If a hand
looks wrong, the phone may have been handed over before the previous player finished their turn.</p>

<h2>Online play feels slow</h2>
<p>The table waits for every phone before showing the next move, so one person on a weak connection
paces everyone. Moves are tiny and the app reconnects by itself. If the leader's phone leaves the
table, the room closes.</p>

<h2>Notifications</h2>
<p>The app can remind you that a table is waiting — at most once every three hours, and never between
10pm and 8am. Turn it off any time under Settings; nothing is sent when it is off. On Android 13 and
above, the permission is asked once right after the first-run terms screen, and again from the
Settings switch if you declined it then. The reminders arrive even when the app is closed; they stop
if you turn the switch off, and a restart of the phone clears them until you next open the app.</p>

<h2>How do the faces beside the names work?</h2>
<p>Every player has an avatar, so a family table looks like a family table instead of a list of
names. If you choose nothing, the app gives you one of twelve faces it draws itself, based on your
name — everyone who joins the same room sees the same face for you. If you would rather be
recognised instantly, tap your face on the home screen (or Settings → Your face) and choose
<strong>Use a photo from my phone</strong>: Android's own picture chooser opens, the middle square of
the picture you pick is cut out and shrunk, and it is stored inside the app. Nothing reads your
gallery, and no photo permission is asked for. In an online table of twelve or fewer players your
picture is shown to the players in that room; in bigger rooms, and offline, only the built-in face
travels. <strong>Remove my photo</strong> takes it back to a face.</p>

<h2>Ads</h2>
<p>The free version shows ads on the menus, never while a hand is being played. Ads are the only
thing funding the relay server that online tables use.</p>

<h2>Rules in your language</h2>
<p>Every game is documented on our <a href="rules.html">how to play</a> page in twelve languages,
and the same explainer is inside the app under <strong>How to play</strong>.</p>

<h2>Still stuck?</h2>
<p>Email <a href="mailto:{EMAIL}">{EMAIL}</a> with your phone model, the Android version, and what
you were doing when it went wrong. If it happened online, include the room code if you have it.</p>
"""
    write("support.html", page("Support", support))
    written.append("support.html")

    # ---------------- /join deep link ----------------
    join = f"""
<h1>You have been invited to a card table</h1>
<p class="tag">Balkrishna Cards — one deck, every game.</p>
<div class="card">
<p id="codeLine">Room code: <strong id="code">—</strong></p>
<p>If the app is installed, it should already be opening. If not, install it and enter the code
above — the app will take you straight to the table.</p>
<a class="btn" href="{PLAY_URL}">Get Balkrishna Cards on Google Play</a>
</div>
<div class="card">
<p class="small">This page is the invite link target for
<code>{DOMAIN}/join?room=CODE</code>. Install the app first, then reopen the link to jump straight
into the room.</p>
</div>
<script>
(function () {{
  var code = new URLSearchParams(location.search).get('room');
  if (code) {{
    document.getElementById('code').textContent = code.toUpperCase();
    // Try the app's deep link first; the Play Store button above is the fallback.
    setTimeout(function () {{ location.href = 'balkrishnacards://join?room=' + encodeURIComponent(code); }}, 400);
  }}
}})();
</script>
"""
    write("join.html", page("Join a table", join, updated="12 September 2026"))
    written.append("join.html")

    # ---------------- assetlinks + robots, so App Links work ----------------
    assetlinks = """[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.balkrishna.cards",
      "sha256_cert_fingerprints": [
        "REPLACE_WITH_YOUR_APP_SIGNING_SHA256_FINGERPRINT"
      ]
    }
  }
]"""
    write(".well-known/assetlinks.json", assetlinks)
    written.append(".well-known/assetlinks.json")

    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    write("sitemap.xml", "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ] + [f"  <url><loc>{DOMAIN}/{p}</loc></url>" for p in
         ["index.html", "rules.html", "terms.html", "privacy.html", "delete-account.html", "support.html", "join.html"]]
      + ["</urlset>"]))
    written += ["robots.txt", "sitemap.xml"]

    write("README.md", f"""# {APP_NAME} website

Deploy this folder to **{DOMAIN}** (HTTPS is required — the app's relay URL and the WhatsApp
invite App Link both assume it).

## Pages

| File | Purpose |
|---|---|
| `index.html` | Home / marketing |
| `rules.html` | How to play every game, in twelve languages (generated from the app's own translations) |
| `terms.html` | Terms & Conditions (required by Play) |
| `privacy.html` | Privacy Policy (required by Play) |
| `delete-account.html` | Data deletion instructions (required by Play for apps with accounts/server data) |
| `support.html` | FAQ and contact |
| `join.html` | Target of the WhatsApp invite link: `{DOMAIN}/join?room=CODE` |
| `.well-known/assetlinks.json` | Digital Asset Links — needed for the `/join` App Link |

Regenerate everything (rules are pulled from the app so the two can never disagree):

```bash
python3 website/build_site.py
```

## Hosting

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, or nginx on your own VPS).
Two things must be true:

1. **HTTPS**, with a valid certificate.
2. The relay runs on the same domain under `/relay`, because the app's default server URL is
   `{DOMAIN}/relay`. With nginx:

```nginx
location /relay/ {{
    proxy_pass http://127.0.0.1:8787/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 40s;      # the relay long-polls for up to 25s
}}
location /.well-known/ {{ root /var/www/balkrishnagames; }}
location / {{ root /var/www/balkrishnagames; try_files $uri $uri/ =404; }}
```

Start the relay with `node server/server.js` (see `docs/20_BUILD_AND_RUN.md`).

## App Links (so an invite opens the app)

1. Put your Play App Signing SHA-256 fingerprint into `.well-known/assetlinks.json`
   (Play Console → Release → Setup → App signing).
2. Add the intent filter to the Android manifest
   (see `docs/20_BUILD_AND_RUN.md`, section "WhatsApp invites").
3. Verify with `https://{DOMAIN}/.well-known/assetlinks.json` and Google's
   [Statement List Generator](https://developers.google.com/digital-asset-links/tools/generator).

Until App Links are verified, the invite link still works: it opens `join.html`, which shows the
room code and offers the Play Store listing.
""")
    written.append("README.md")

    print("wrote:")
    for w in written:
        print("  website/" + w)


def write(rel, text):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    build()

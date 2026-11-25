"""Bot UI strings in English, Kannada and Hindi. Add a language by adding a column to every key."""

LANGS = {"en": "English", "kn": "ಕನ್ನಡ", "hi": "हिन्दी"}

CHOOSE_LANGUAGE = "🌐 Choose your language\nನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ\nअपनी भाषा चुनें"

S = {
    "lang_set": {"en": "✅ Language: English", "kn": "✅ ಭಾಷೆ: ಕನ್ನಡ", "hi": "✅ भाषा: हिन्दी"},
    "welcome": {
        "en": "👋 Welcome to <b>BloodLink</b>! Request blood or become a donor in a few taps.",
        "kn": "👋 <b>BloodLink</b>ಗೆ ಸ್ವಾಗತ! ಕೆಲವೇ ಟ್ಯಾಪ್‌ಗಳಲ್ಲಿ ರಕ್ತ ವಿನಂತಿಸಿ ಅಥವಾ ದಾನಿಯಾಗಿ.",
        "hi": "👋 <b>BloodLink</b> में आपका स्वागत है! कुछ ही टैप में खून का अनुरोध करें या डोनर बनें।",
    },
    "welcome_back": {
        "en": "👋 Welcome back, <b>{name}</b>!",
        "kn": "👋 ಮರಳಿ ಸ್ವಾಗತ, <b>{name}</b>!",
        "hi": "👋 फिर से स्वागत है, <b>{name}</b>!",
    },
    "menu_prompt": {"en": "What would you like to do?", "kn": "ನೀವು ಏನು ಮಾಡಲು ಬಯಸುತ್ತೀರಿ?", "hi": "आप क्या करना चाहेंगे?"},
    "btn_sos": {"en": "🚨 Request Blood (SOS)", "kn": "🚨 ರಕ್ತ ವಿನಂತಿ (SOS)", "hi": "🚨 खून का अनुरोध (SOS)"},
    "btn_register": {"en": "🩸 Become a Donor", "kn": "🩸 ದಾನಿಯಾಗಿ", "hi": "🩸 डोनर बनें"},
    "btn_requests": {"en": "📋 Active Requests", "kn": "📋 ಸಕ್ರಿಯ ವಿನಂತಿಗಳು", "hi": "📋 सक्रिय अनुरोध"},
    "btn_me": {"en": "👤 My Profile", "kn": "👤 ನನ್ನ ಪ್ರೊಫೈಲ್", "hi": "👤 मेरी प्रोफ़ाइल"},
    "btn_invite": {"en": "🤝 Invite Friends", "kn": "🤝 ಸ್ನೇಹಿತರನ್ನು ಆಹ್ವಾನಿಸಿ", "hi": "🤝 दोस्तों को बुलाएँ"},
    "btn_rewards": {"en": "🎁 Rewards", "kn": "🎁 ಬಹುಮಾನಗಳು", "hi": "🎁 इनाम"},
    "btn_leaderboard": {"en": "🏆 Leaderboard", "kn": "🏆 ಲೀಡರ್‌ಬೋರ್ಡ್", "hi": "🏆 लीडरबोर्ड"},
    "btn_achievements": {"en": "🏅 Achievements", "kn": "🏅 ಸಾಧನೆಗಳು", "hi": "🏅 उपलब्धियाँ"},
    "btn_location": {"en": "📍 Nearby alerts", "kn": "📍 ಹತ್ತಿರದ ಎಚ್ಚರಿಕೆಗಳು", "hi": "📍 पास के अलर्ट"},
    "btn_send_location": {"en": "📍 Share my location", "kn": "📍 ನನ್ನ ಸ್ಥಳ ಹಂಚಿಕೊಳ್ಳಿ", "hi": "📍 मेरी लोकेशन भेजें"},
    "ask_location": {
        "en": "📍 Share your location once and we'll alert you first for emergencies near you.\n"
              "We round it to about 1 km and never show it to anyone. Tap the button below (or Skip).",
        "kn": "📍 ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಒಮ್ಮೆ ಹಂಚಿಕೊಳ್ಳಿ, ನಿಮ್ಮ ಹತ್ತಿರದ ತುರ್ತುಗಳಿಗೆ ಮೊದಲು ನಿಮಗೆ ಎಚ್ಚರಿಕೆ ಕಳುಹಿಸುತ್ತೇವೆ.\n"
              "ಇದನ್ನು ಸುಮಾರು 1 ಕಿಮೀಗೆ ಸರಿಹೊಂದಿಸುತ್ತೇವೆ ಮತ್ತು ಯಾರಿಗೂ ತೋರಿಸುವುದಿಲ್ಲ. ಕೆಳಗಿನ ಬಟನ್ ಒತ್ತಿ (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ).",
        "hi": "📍 एक बार अपनी लोकेशन भेजें, ताकि पास की आपात स्थिति में सबसे पहले आपको अलर्ट मिले।\n"
              "हम इसे लगभग 1 किमी तक गोल करते हैं और किसी को नहीं दिखाते। नीचे बटन दबाएँ (या छोड़ें)।",
    },
    "location_saved": {"en": "✅ Saved (approximately). You'll be alerted first for emergencies near you.",
                       "kn": "✅ ಉಳಿಸಲಾಗಿದೆ (ಅಂದಾಜು). ನಿಮ್ಮ ಹತ್ತಿರದ ತುರ್ತುಗಳಿಗೆ ಮೊದಲು ಎಚ್ಚರಿಕೆ ಬರುತ್ತದೆ.",
                       "hi": "✅ सेव हो गया (लगभग)। पास की आपात स्थिति में सबसे पहले आपको अलर्ट मिलेगा।"},
    "btn_camps": {"en": "🏕️ Camps", "kn": "🏕️ ಶಿಬಿರಗಳು", "hi": "🏕️ कैंप"},
    "btn_teams": {"en": "👥 My Teams", "kn": "👥 ನನ್ನ ತಂಡಗಳು", "hi": "👥 मेरी टीमें"},
    "btn_rsvp": {"en": "✅ RSVP", "kn": "✅ ನೋಂದಾಯಿಸಿ", "hi": "✅ RSVP करें"},
    "btn_unrsvp": {"en": "✖ Cancel RSVP", "kn": "✖ ನೋಂದಣಿ ರದ್ದು", "hi": "✖ RSVP रद्द करें"},
    "camps_title": {"en": "🏕️ <b>UPCOMING DONATION CAMPS</b>", "kn": "🏕️ <b>ಮುಂಬರುವ ರಕ್ತದಾನ ಶಿಬಿರಗಳು</b>",
                    "hi": "🏕️ <b>आने वाले रक्तदान कैंप</b>"},
    "camps_none": {"en": "No upcoming camps near you yet. Organise one on the website: {url}",
                   "kn": "ನಿಮ್ಮ ಹತ್ತಿರ ಇನ್ನೂ ಶಿಬಿರಗಳಿಲ್ಲ. ವೆಬ್‌ಸೈಟ್‌ನಲ್ಲಿ ಒಂದನ್ನು ಆಯೋಜಿಸಿ: {url}",
                   "hi": "आपके पास अभी कोई कैंप नहीं। वेबसाइट पर एक आयोजित करें: {url}"},
    "camp_going": {"en": "✅ You're going", "kn": "✅ ನೀವು ಬರುತ್ತಿದ್ದೀರಿ", "hi": "✅ आप आ रहे हैं"},
    "rsvp_ok": {"en": "✅ Registered! We'll remind you.", "kn": "✅ ನೋಂದಣಿ ಆಯಿತು! ನೆನಪಿಸುತ್ತೇವೆ.", "hi": "✅ रजिस्टर हो गया! हम याद दिलाएँगे।"},
    "rsvp_cancel": {"en": "RSVP cancelled.", "kn": "ನೋಂದಣಿ ರದ್ದಾಗಿದೆ.", "hi": "RSVP रद्द किया गया।"},
    "teams_title": {"en": "👥 <b>YOUR TEAMS</b>", "kn": "👥 <b>ನಿಮ್ಮ ತಂಡಗಳು</b>", "hi": "👥 <b>आपकी टीमें</b>"},
    "teams_none": {"en": "You're not in a team yet. Join your college or company team (or start one) at {url}",
                   "kn": "ನೀವು ಇನ್ನೂ ಯಾವುದೇ ತಂಡದಲ್ಲಿಲ್ಲ. ನಿಮ್ಮ ಕಾಲೇಜು ಅಥವಾ ಕಂಪನಿ ತಂಡ ಸೇರಿ (ಅಥವಾ ಹೊಸದು ಆರಂಭಿಸಿ): {url}",
                   "hi": "आप अभी किसी टीम में नहीं हैं। अपने कॉलेज या कंपनी की टीम से जुड़ें (या नई बनाएँ): {url}"},
    "team_line": {"en": "#{rank} <b>{name}</b> · {points} BLP · {donations} donations · {members} members",
                  "kn": "#{rank} <b>{name}</b> · {points} BLP · {donations} ದಾನ · {members} ಸದಸ್ಯರು",
                  "hi": "#{rank} <b>{name}</b> · {points} BLP · {donations} रक्तदान · {members} सदस्य"},
    "btn_language": {"en": "🌐 Language", "kn": "🌐 ಭಾಷೆ", "hi": "🌐 भाषा"},
    "btn_available": {"en": "🟢 I'm available", "kn": "🟢 ನಾನು ಲಭ್ಯವಿದ್ದೇನೆ", "hi": "🟢 मैं उपलब्ध हूँ"},
    "btn_busy": {"en": "⚪ Pause alerts", "kn": "⚪ ಎಚ್ಚರಿಕೆಗಳನ್ನು ನಿಲ್ಲಿಸಿ", "hi": "⚪ अलर्ट रोकें"},
    "btn_menu": {"en": "🏠 Menu", "kn": "🏠 ಮೆನು", "hi": "🏠 मेनू"},
    "btn_back": {"en": "⬅️ Back", "kn": "⬅️ ಹಿಂದೆ", "hi": "⬅️ पीछे"},
    "btn_cancel": {"en": "✖️ Cancel", "kn": "✖️ ರದ್ದುಮಾಡಿ", "hi": "✖️ रद्द करें"},
    "btn_other": {"en": "✏️ Other (type)", "kn": "✏️ ಇತರೆ (ಟೈಪ್ ಮಾಡಿ)", "hi": "✏️ अन्य (टाइप करें)"},
    "btn_skip": {"en": "Skip ➡️", "kn": "ಬಿಟ್ಟುಬಿಡಿ ➡️", "hi": "छोड़ें ➡️"},
    "btn_share_phone": {"en": "📱 Share my phone number", "kn": "📱 ನನ್ನ ಫೋನ್ ಸಂಖ್ಯೆ ಹಂಚಿಕೊಳ್ಳಿ",
                        "hi": "📱 मेरा फ़ोन नंबर साझा करें"},
    "btn_donate": {"en": "🩸 I Can Donate", "kn": "🩸 ನಾನು ದಾನ ಮಾಡಬಲ್ಲೆ", "hi": "🩸 मैं रक्तदान करूँगा/करूँगी"},
    "btn_use_name": {"en": "✅ Use “{name}”", "kn": "✅ “{name}” ಬಳಸಿ", "hi": "✅ “{name}” इस्तेमाल करें"},
    "invited": {
        "en": "🎉 You were invited with code <code>{code}</code>! Register to get a <b>+50 BLP welcome bonus</b>.",
        "kn": "🎉 ನಿಮ್ಮನ್ನು <code>{code}</code> ಕೋಡ್ ಮೂಲಕ ಆಹ್ವಾನಿಸಲಾಗಿದೆ! ನೋಂದಾಯಿಸಿ ಮತ್ತು <b>+50 BLP ಸ್ವಾಗತ ಬೋನಸ್</b> ಪಡೆಯಿರಿ.",
        "hi": "🎉 आपको कोड <code>{code}</code> से आमंत्रित किया गया है! रजिस्टर करें और <b>+50 BLP स्वागत बोनस</b> पाएँ।",
    },
    "linked": {
        "en": "✅ Telegram linked to <b>{name}</b>! You'll now get SOS alerts for compatible requests.",
        "kn": "✅ Telegram ಅನ್ನು <b>{name}</b> ಖಾತೆಗೆ ಲಿಂಕ್ ಮಾಡಲಾಗಿದೆ! ಹೊಂದಾಣಿಕೆಯ ವಿನಂತಿಗಳ SOS ಎಚ್ಚರಿಕೆಗಳನ್ನು ನೀವು ಪಡೆಯುತ್ತೀರಿ.",
        "hi": "✅ Telegram <b>{name}</b> के खाते से जुड़ गया! अब आपको मेल खाते अनुरोधों के SOS अलर्ट मिलेंगे।",
    },
    "already_registered": {"en": "You're already registered! ✅", "kn": "ನೀವು ಈಗಾಗಲೇ ನೋಂದಾಯಿಸಿದ್ದೀರಿ! ✅",
                           "hi": "आप पहले से रजिस्टर्ड हैं! ✅"},
    "reg_name": {
        "en": "🩸 Let's register you as a donor.\n\nWhat's your <b>name</b>? Tap the button or type it.",
        "kn": "🩸 ನಿಮ್ಮನ್ನು ದಾನಿಯಾಗಿ ನೋಂದಾಯಿಸೋಣ.\n\nನಿಮ್ಮ <b>ಹೆಸರು</b> ಏನು? ಬಟನ್ ಒತ್ತಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ.",
        "hi": "🩸 चलिए आपको डोनर के रूप में रजिस्टर करते हैं।\n\nआपका <b>नाम</b> क्या है? बटन दबाएँ या टाइप करें।",
    },
    "reg_group": {"en": "Select your <b>blood group</b>:", "kn": "ನಿಮ್ಮ <b>ರಕ್ತದ ಗುಂಪು</b> ಆಯ್ಕೆಮಾಡಿ:",
                  "hi": "अपना <b>ब्लड ग्रुप</b> चुनें:"},
    "choose_state": {"en": "📍 Select your <b>state</b>:", "kn": "📍 ನಿಮ್ಮ <b>ರಾಜ್ಯ</b> ಆಯ್ಕೆಮಾಡಿ:",
                     "hi": "📍 अपना <b>राज्य</b> चुनें:"},
    "choose_district": {"en": "📍 <b>{state}</b> — select the <b>district</b>:",
                        "kn": "📍 <b>{state}</b> — <b>ಜಿಲ್ಲೆ</b> ಆಯ್ಕೆಮಾಡಿ:",
                        "hi": "📍 <b>{state}</b> — <b>ज़िला</b> चुनें:"},
    "type_city": {"en": "Type your <b>city / district</b> name:", "kn": "ನಿಮ್ಮ <b>ನಗರ / ಜಿಲ್ಲೆಯ</b> ಹೆಸರನ್ನು ಟೈಪ್ ಮಾಡಿ:",
                  "hi": "अपने <b>शहर / ज़िले</b> का नाम टाइप करें:"},
    "reg_phone": {
        "en": "📱 Share your phone number so the hospital can contact you when you respond? (optional)",
        "kn": "📱 ನೀವು ಪ್ರತಿಕ್ರಿಯಿಸಿದಾಗ ಆಸ್ಪತ್ರೆ ನಿಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸಲು ಫೋನ್ ಸಂಖ್ಯೆ ಹಂಚಿಕೊಳ್ಳುವಿರಾ? (ಐಚ್ಛಿಕ)",
        "hi": "📱 जवाब देने पर अस्पताल आपसे संपर्क कर सके, इसके लिए फ़ोन नंबर साझा करेंगे? (वैकल्पिक)",
    },
    "reg_sex": {"en": "🩺 A few health questions decide whether you can donate safely.\n\nYou are:",
                "kn": "🩺 ನೀವು ಸುರಕ್ಷಿತವಾಗಿ ರಕ್ತದಾನ ಮಾಡಬಹುದೇ ಎಂದು ಕೆಲವು ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಗಳು ನಿರ್ಧರಿಸುತ್ತವೆ.\n\nನೀವು:",
                "hi": "🩺 कुछ स्वास्थ्य प्रश्न तय करते हैं कि आप सुरक्षित रूप से रक्तदान कर सकते हैं या नहीं।\n\nआप हैं:"},
    "sex_male": {"en": "👨 Male", "kn": "👨 ಪುರುಷ", "hi": "👨 पुरुष"},
    "sex_female": {"en": "👩 Female", "kn": "👩 ಮಹಿಳೆ", "hi": "👩 महिला"},
    "sex_other": {"en": "Other", "kn": "ಇತರ", "hi": "अन्य"},
    "reg_dob": {"en": "🎂 Your date of birth? Type it like <b>14-08-1998</b>.\n(Donors must be 18 to 65.)",
                "kn": "🎂 ನಿಮ್ಮ ಜನ್ಮ ದಿನಾಂಕ? <b>14-08-1998</b> ಹೀಗೆ ಟೈಪ್ ಮಾಡಿ.\n(ದಾನಿಗಳು 18 ರಿಂದ 65 ವರ್ಷದವರಾಗಿರಬೇಕು.)",
                "hi": "🎂 आपकी जन्म तिथि? ऐसे लिखें: <b>14-08-1998</b>\n(दाता की उम्र 18 से 65 वर्ष होनी चाहिए।)"},
    "reg_dob_bad": {"en": "Please type the date like 14-08-1998.", "kn": "ದಯವಿಟ್ಟು ದಿನಾಂಕವನ್ನು 14-08-1998 ಹೀಗೆ ಟೈಪ್ ಮಾಡಿ.",
                    "hi": "कृपया तिथि ऐसे लिखें: 14-08-1998"},
    "reg_weight": {"en": "⚖️ Your weight? (Donors must weigh at least 45 kg.)",
                   "kn": "⚖️ ನಿಮ್ಮ ತೂಕ? (ದಾನಿಗಳು ಕನಿಷ್ಠ 45 ಕೆಜಿ ಇರಬೇಕು.)",
                   "hi": "⚖️ आपका वज़न? (दाता का वज़न कम से कम 45 किलो होना चाहिए।)"},
    "weight_under": {"en": "Under 45 kg", "kn": "45 ಕೆಜಿಗಿಂತ ಕಡಿಮೆ", "hi": "45 किलो से कम"},
    "reg_conditions": {
        "en": "🧬 <b>Permanent conditions</b>\nPeople with any of these can never donate, to protect both them and the patient:\n\n"
              "• Thalassaemia major or intermedia (the trait is fine)\n• Sickle cell disease\n"
              "• Haemophilia or another bleeding disorder\n• HIV / AIDS\n• Hepatitis B or C (ever)\n"
              "• Heart disease: heart attack, angina or heart surgery\n• Cancer (now or in the past)\n"
              "• Epilepsy or fits on treatment\n• Chronic kidney or liver disease\n• Diabetes treated with insulin\n\n"
              "We only save whether one applies, never which one.",
        "kn": "🧬 <b>ಶಾಶ್ವತ ಆರೋಗ್ಯ ಸ್ಥಿತಿಗಳು</b>\nಇವುಗಳಲ್ಲಿ ಯಾವುದಾದರೂ ಇದ್ದರೆ, ನಿಮ್ಮ ಮತ್ತು ರೋಗಿಯ ಸುರಕ್ಷತೆಗಾಗಿ ಎಂದಿಗೂ ರಕ್ತದಾನ ಮಾಡಲಾಗದು:\n\n"
              "• ಥಲಸ್ಸೇಮಿಯಾ ಮೇಜರ್ ಅಥವಾ ಇಂಟರ್ಮೀಡಿಯಾ (ಟ್ರೇಟ್ ಇದ್ದರೆ ಪರವಾಗಿಲ್ಲ)\n• ಸಿಕಲ್ ಸೆಲ್ ಕಾಯಿಲೆ\n"
              "• ಹಿಮೋಫಿಲಿಯಾ ಅಥವಾ ಇತರ ರಕ್ತಸ್ರಾವ ಕಾಯಿಲೆ\n• ಎಚ್ಐವಿ / ಏಡ್ಸ್\n• ಹೆಪಟೈಟಿಸ್ ಬಿ ಅಥವಾ ಸಿ (ಎಂದಾದರೂ)\n"
              "• ಹೃದಯ ಕಾಯಿಲೆ: ಹೃದಯಾಘಾತ, ಎದೆನೋವು ಅಥವಾ ಹೃದಯ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ\n• ಕ್ಯಾನ್ಸರ್ (ಈಗ ಅಥವಾ ಹಿಂದೆ)\n"
              "• ಚಿಕಿತ್ಸೆಯಲ್ಲಿರುವ ಅಪಸ್ಮಾರ ಅಥವಾ ಮೂರ್ಛೆ\n• ದೀರ್ಘಕಾಲದ ಮೂತ್ರಪಿಂಡ ಅಥವಾ ಯಕೃತ್ತಿನ ಕಾಯಿಲೆ\n• ಇನ್ಸುಲಿನ್ ಬಳಸುವ ಮಧುಮೇಹ\n\n"
              "ಇವುಗಳಲ್ಲಿ ಒಂದು ಇದೆಯೇ ಎಂಬುದನ್ನು ಮಾತ್ರ ಉಳಿಸುತ್ತೇವೆ, ಯಾವುದು ಎಂಬುದನ್ನಲ್ಲ.",
        "hi": "🧬 <b>स्थायी स्वास्थ्य स्थितियाँ</b>\nइनमें से कोई भी होने पर, आपकी और मरीज़ की सुरक्षा के लिए कभी रक्तदान नहीं किया जा सकता:\n\n"
              "• थैलेसीमिया मेजर या इंटरमीडिया (ट्रेट होने पर ठीक है)\n• सिकल सेल रोग\n"
              "• हीमोफ़ीलिया या कोई अन्य रक्तस्राव विकार\n• एचआईवी / एड्स\n• हेपेटाइटिस बी या सी (कभी भी)\n"
              "• हृदय रोग: दिल का दौरा, एनजाइना या हृदय की सर्जरी\n• कैंसर (अभी या पहले)\n"
              "• इलाज चल रहा मिर्गी या दौरे\n• लंबे समय से गुर्दे या लिवर की बीमारी\n• इंसुलिन से इलाज वाला मधुमेह\n\n"
              "हम केवल यह सहेजते हैं कि इनमें से कोई लागू है या नहीं, कौन-सा यह नहीं।",
    },
    "cond_none_btn": {"en": "✅ None of these apply", "kn": "✅ ಇವುಗಳಲ್ಲಿ ಯಾವುದೂ ಇಲ್ಲ", "hi": "✅ इनमें से कोई लागू नहीं"},
    "cond_any_btn": {"en": "⚠️ One of these applies", "kn": "⚠️ ಇವುಗಳಲ್ಲಿ ಒಂದು ಇದೆ", "hi": "⚠️ इनमें से एक लागू है"},
    "reg_cannot_donate": {
        "en": "💙 Thank you for being honest. With that condition, donating isn't safe for you or the patient, so we "
              "won't send you blood alerts. You can still request blood, invite friends and join camps.",
        "kn": "💙 ಪ್ರಾಮಾಣಿಕತೆಗೆ ಧನ್ಯವಾದ. ಆ ಸ್ಥಿತಿಯೊಂದಿಗೆ ರಕ್ತದಾನ ನಿಮಗೂ ರೋಗಿಗೂ ಸುರಕ್ಷಿತವಲ್ಲ, ಆದ್ದರಿಂದ ನಿಮಗೆ ರಕ್ತದ ಎಚ್ಚರಿಕೆಗಳನ್ನು "
              "ಕಳುಹಿಸುವುದಿಲ್ಲ. ನೀವು ಇನ್ನೂ ರಕ್ತಕ್ಕಾಗಿ ವಿನಂತಿಸಬಹುದು, ಸ್ನೇಹಿತರನ್ನು ಆಹ್ವಾನಿಸಬಹುದು ಮತ್ತು ಶಿಬಿರಗಳಿಗೆ ಸೇರಬಹುದು.",
        "hi": "💙 ईमानदारी के लिए धन्यवाद। उस स्थिति में रक्तदान न आपके लिए सुरक्षित है न मरीज़ के लिए, इसलिए हम आपको "
              "रक्त अलर्ट नहीं भेजेंगे। आप फिर भी रक्त का अनुरोध कर सकते हैं, दोस्तों को बुला सकते हैं और शिविरों में शामिल हो सकते हैं।",
    },
    "elig_permanent": {
        "en": "💙 Your health check says donating isn't safe for you, so you can't pledge. If that was a mistake, "
              "you can redo the check on your profile: {url}",
        "kn": "💙 ನಿಮ್ಮ ಆರೋಗ್ಯ ಪರಿಶೀಲನೆಯ ಪ್ರಕಾರ ರಕ್ತದಾನ ನಿಮಗೆ ಸುರಕ್ಷಿತವಲ್ಲ, ಆದ್ದರಿಂದ ವಾಗ್ದಾನ ಮಾಡಲಾಗದು. ತಪ್ಪಾಗಿದ್ದರೆ, "
              "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನಲ್ಲಿ ಮತ್ತೆ ಪರಿಶೀಲಿಸಿ: {url}",
        "hi": "💙 आपकी स्वास्थ्य जाँच के अनुसार रक्तदान आपके लिए सुरक्षित नहीं है, इसलिए आप वादा नहीं कर सकते। अगर यह गलती थी, "
              "तो अपनी प्रोफ़ाइल पर जाँच दोबारा करें: {url}",
    },
    "reg_done": {
        "en": "🎉 <b>Welcome to BloodLink, {name}!</b>\nYou earned <b>{points} BLP</b>{bonus}.\n"
              "You'll get an alert when someone near {district} needs blood you can give.",
        "kn": "🎉 <b>BloodLinkಗೆ ಸ್ವಾಗತ, {name}!</b>\nನೀವು <b>{points} BLP</b> ಗಳಿಸಿದ್ದೀರಿ{bonus}.\n"
              "{district} ಬಳಿ ಯಾರಿಗಾದರೂ ನೀವು ನೀಡಬಹುದಾದ ರಕ್ತ ಬೇಕಾದಾಗ ನಿಮಗೆ ಎಚ್ಚರಿಕೆ ಬರುತ್ತದೆ.",
        "hi": "🎉 <b>BloodLink में स्वागत है, {name}!</b>\nआपने <b>{points} BLP</b> कमाए{bonus}।\n"
              "{district} के पास किसी को आपके दिए जा सकने वाले खून की ज़रूरत होगी तो आपको अलर्ट मिलेगा।",
    },
    "bonus": {"en": " (incl. +50 welcome bonus 🎁)", "kn": " (+50 ಸ್ವಾಗತ ಬೋನಸ್ ಸೇರಿ 🎁)", "hi": " (+50 स्वागत बोनस सहित 🎁)"},
    "invite": {
        "en": "🤝 <b>Invite a friend, earn a voucher!</b>\n\nShare this link:\n{link}\n\n"
              "• Friend registers → you get <b>+50 BLP</b>\n• Friend donates → you get <b>+200 BLP + a voucher</b>",
        "kn": "🤝 <b>ಸ್ನೇಹಿತರನ್ನು ಆಹ್ವಾನಿಸಿ, ವೋಚರ್ ಗಳಿಸಿ!</b>\n\nಈ ಲಿಂಕ್ ಹಂಚಿಕೊಳ್ಳಿ:\n{link}\n\n"
              "• ಸ್ನೇಹಿತ ನೋಂದಾಯಿಸಿದರೆ → ನಿಮಗೆ <b>+50 BLP</b>\n• ಸ್ನೇಹಿತ ರಕ್ತದಾನ ಮಾಡಿದರೆ → ನಿಮಗೆ <b>+200 BLP + ವೋಚರ್</b>",
        "hi": "🤝 <b>दोस्त को बुलाएँ, वाउचर पाएँ!</b>\n\nयह लिंक साझा करें:\n{link}\n\n"
              "• दोस्त रजिस्टर करे → आपको <b>+50 BLP</b>\n• दोस्त रक्तदान करे → आपको <b>+200 BLP + वाउचर</b>",
    },
    "sos_group": {
        "en": "🚨 <b>Emergency blood request</b>\n\nWhich <b>blood group</b> is needed?",
        "kn": "🚨 <b>ತುರ್ತು ರಕ್ತ ವಿನಂತಿ</b>\n\nಯಾವ <b>ರಕ್ತದ ಗುಂಪು</b> ಬೇಕು?",
        "hi": "🚨 <b>आपातकालीन खून अनुरोध</b>\n\nकौन सा <b>ब्लड ग्रुप</b> चाहिए?",
    },
    "sos_state": {"en": "📍 Where is the patient? Select the <b>state</b>:",
                  "kn": "📍 ರೋಗಿ ಎಲ್ಲಿದ್ದಾರೆ? <b>ರಾಜ್ಯ</b> ಆಯ್ಕೆಮಾಡಿ:",
                  "hi": "📍 मरीज़ कहाँ है? <b>राज्य</b> चुनें:"},
    "sos_hospital": {"en": "🏥 Select the <b>hospital</b> in {district}:",
                     "kn": "🏥 {district} ನಲ್ಲಿರುವ <b>ಆಸ್ಪತ್ರೆ</b> ಆಯ್ಕೆಮಾಡಿ:",
                     "hi": "🏥 {district} में <b>अस्पताल</b> चुनें:"},
    "type_hospital": {"en": "Type the <b>hospital name</b>:", "kn": "<b>ಆಸ್ಪತ್ರೆಯ ಹೆಸರು</b> ಟೈಪ್ ಮಾಡಿ:",
                      "hi": "<b>अस्पताल का नाम</b> टाइप करें:"},
    "type_hospital_city": {
        "en": "Type the <b>hospital and city</b>, e.g. <i>City Hospital, Hyderabad</i>",
        "kn": "<b>ಆಸ್ಪತ್ರೆ ಮತ್ತು ನಗರ</b> ಟೈಪ್ ಮಾಡಿ, ಉದಾ: <i>City Hospital, Hyderabad</i>",
        "hi": "<b>अस्पताल और शहर</b> टाइप करें, जैसे <i>City Hospital, Hyderabad</i>",
    },
    "need_comma": {"en": "Please send it as <b>Hospital, City</b>", "kn": "ದಯವಿಟ್ಟು <b>ಆಸ್ಪತ್ರೆ, ನಗರ</b> ರೂಪದಲ್ಲಿ ಕಳುಹಿಸಿ",
                   "hi": "कृपया <b>अस्पताल, शहर</b> के रूप में भेजें"},
    "sos_units": {"en": "🩸 How many <b>units</b> are needed?", "kn": "🩸 ಎಷ್ಟು <b>ಯೂನಿಟ್‌</b> ಬೇಕು?",
                  "hi": "🩸 कितने <b>यूनिट</b> चाहिए?"},
    "sos_urgency": {"en": "⏱ How <b>urgent</b> is it?", "kn": "⏱ ಎಷ್ಟು <b>ತುರ್ತು</b>?", "hi": "⏱ कितना <b>ज़रूरी</b> है?"},
    "urg_Critical": {"en": "🔴 Critical (within hours)", "kn": "🔴 ಅತಿ ತುರ್ತು (ಕೆಲವೇ ಗಂಟೆಗಳಲ್ಲಿ)",
                     "hi": "🔴 बहुत ज़रूरी (कुछ घंटों में)"},
    "urg_High": {"en": "🟠 Needed today", "kn": "🟠 ಇಂದೇ ಬೇಕು", "hi": "🟠 आज ही चाहिए"},
    "urg_Normal": {"en": "🟡 Planned surgery", "kn": "🟡 ಯೋಜಿತ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ", "hi": "🟡 तय ऑपरेशन"},
    "sos_phone": {
        "en": "📱 Share a contact number for donors? (recommended)",
        "kn": "📱 ದಾನಿಗಳಿಗಾಗಿ ಸಂಪರ್ಕ ಸಂಖ್ಯೆ ಹಂಚಿಕೊಳ್ಳುವಿರಾ? (ಶಿಫಾರಸು)",
        "hi": "📱 डोनरों के लिए संपर्क नंबर साझा करेंगे? (सुझाया गया)",
    },
    "working": {"en": "⏳ One moment…", "kn": "⏳ ಸ್ವಲ್ಪ ನಿರೀಕ್ಷಿಸಿ…", "hi": "⏳ एक पल…"},
    "sos_done": {
        "en": "🚨 <b>SOS BROADCASTED</b>\n\n🩸 {units} × <b>{group}</b>\n🏥 {hospital}, {district}\n\n"
              "👥 <b>{matched}</b> compatible donors matched, <b>{alerted}</b> alerted on Telegram.\n"
              "Request #{id}. You'll be notified here as donors respond.\n\n"
              "⚠️ Compatibility is preliminary; the hospital confirms eligibility.",
        "kn": "🚨 <b>SOS ಪ್ರಸಾರವಾಗಿದೆ</b>\n\n🩸 {units} × <b>{group}</b>\n🏥 {hospital}, {district}\n\n"
              "👥 <b>{matched}</b> ಹೊಂದಾಣಿಕೆಯ ದಾನಿಗಳು ಸಿಕ್ಕಿದ್ದಾರೆ, <b>{alerted}</b> ಜನರಿಗೆ Telegram ಎಚ್ಚರಿಕೆ ಕಳುಹಿಸಲಾಗಿದೆ.\n"
              "ವಿನಂತಿ #{id}. ದಾನಿಗಳು ಪ್ರತಿಕ್ರಿಯಿಸಿದಾಗ ಇಲ್ಲಿ ತಿಳಿಸಲಾಗುವುದು.\n\n"
              "⚠️ ಹೊಂದಾಣಿಕೆ ಪ್ರಾಥಮಿಕ ಮಾತ್ರ; ಅರ್ಹತೆಯನ್ನು ಆಸ್ಪತ್ರೆ ದೃಢಪಡಿಸುತ್ತದೆ.",
        "hi": "🚨 <b>SOS प्रसारित हो गया</b>\n\n🩸 {units} × <b>{group}</b>\n🏥 {hospital}, {district}\n\n"
              "👥 <b>{matched}</b> मेल खाते डोनर मिले, <b>{alerted}</b> को Telegram पर अलर्ट भेजा गया।\n"
              "अनुरोध #{id}। डोनरों के जवाब देने पर आपको यहीं सूचना मिलेगी।\n\n"
              "⚠️ मिलान प्रारंभिक है; योग्यता अस्पताल तय करता है।",
    },
    "sos_failed": {"en": "⚠️ Could not create the request: {error}", "kn": "⚠️ ವಿನಂತಿ ರಚಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ: {error}",
                   "hi": "⚠️ अनुरोध नहीं बन सका: {error}"},
    "donate_thanks": {"en": "Thank you, hero! 🩸", "kn": "ಧನ್ಯವಾದಗಳು, ಹೀರೋ! 🩸", "hi": "धन्यवाद, हीरो! 🩸"},
    "pledged": {
        "en": "✅ <b>You've pledged for request #{id}</b>\n🏥 {hospital}, {city} — {group}{phone}\n\n"
              "Please go to the hospital with a photo ID. Once staff confirm your donation you'll get about "
              "<b>{points} BLP</b>.\n{lines}\n\nIf nobody confirms it within {hours} hours, the pledge expires.",
        "kn": "✅ <b>ವಿನಂತಿ #{id} ಗೆ ನೀವು ವಾಗ್ದಾನ ಮಾಡಿದ್ದೀರಿ</b>\n🏥 {hospital}, {city} — {group}{phone}\n\n"
              "ದಯವಿಟ್ಟು ಫೋಟೋ ಐಡಿಯೊಂದಿಗೆ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ. ಸಿಬ್ಬಂದಿ ನಿಮ್ಮ ರಕ್ತದಾನವನ್ನು ದೃಢೀಕರಿಸಿದ ನಂತರ ನಿಮಗೆ ಸುಮಾರು "
              "<b>{points} BLP</b> ಸಿಗುತ್ತದೆ.\n{lines}\n\n{hours} ಗಂಟೆಯಲ್ಲಿ ಯಾರೂ ದೃಢೀಕರಿಸದಿದ್ದರೆ, ವಾಗ್ದಾನ ಮುಗಿಯುತ್ತದೆ.",
        "hi": "✅ <b>आपने अनुरोध #{id} के लिए वादा किया है</b>\n🏥 {hospital}, {city} — {group}{phone}\n\n"
              "कृपया फ़ोटो पहचान पत्र के साथ अस्पताल जाएँ। स्टाफ़ द्वारा रक्तदान की पुष्टि के बाद आपको लगभग "
              "<b>{points} BLP</b> मिलेंगे।\n{lines}\n\nअगर {hours} घंटे में कोई पुष्टि नहीं करता, तो वादा समाप्त हो जाएगा।",
    },
    "staff_done": {"en": "✅ Confirmed: {name} gets {points} BLP.", "kn": "✅ ದೃಢೀಕರಿಸಲಾಗಿದೆ: {name} ಗೆ {points} BLP.",
                   "hi": "✅ पुष्टि हुई: {name} को {points} BLP मिले।"},
    "staff_noshow": {"en": "❌ Marked as not come. The donor has been told.",
                     "kn": "❌ ಬರಲಿಲ್ಲ ಎಂದು ಗುರುತಿಸಲಾಗಿದೆ. ದಾನಿಗೆ ತಿಳಿಸಲಾಗಿದೆ.",
                     "hi": "❌ नहीं आए के रूप में दर्ज। दाता को बता दिया गया है।"},
    "staff_lowhb": {"en": "🩸 Recorded as low haemoglobin. {name} gets iron advice and can try again in 30 days.",
                    "kn": "🩸 ಕಡಿಮೆ ಹಿಮೋಗ್ಲೋಬಿನ್ ಎಂದು ದಾಖಲಿಸಲಾಗಿದೆ. {name} ಅವರಿಗೆ ಕಬ್ಬಿಣಾಂಶದ ಸಲಹೆ ಕಳುಹಿಸಲಾಗಿದೆ, 30 ದಿನಗಳ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಬಹುದು.",
                    "hi": "🩸 कम हीमोग्लोबिन के रूप में दर्ज। {name} को आयरन संबंधी सलाह भेजी गई है, वे 30 दिन बाद फिर कोशिश कर सकते हैं।"},
    "contact": {"en": "\n📞 Contact: {phone}", "kn": "\n📞 ಸಂಪರ್ಕ: {phone}", "hi": "\n📞 संपर्क: {phone}"},
    "bd_donation": {"en": "Successful donation", "kn": "ಯಶಸ್ವಿ ರಕ್ತದಾನ", "hi": "सफल रक्तदान"},
    "bd_quick": {"en": "Quick response (< 5 min)", "kn": "ತ್ವರಿತ ಪ್ರತಿಕ್ರಿಯೆ (< 5 ನಿಮಿಷ)", "hi": "तेज़ जवाब (< 5 मिनट)"},
    "bd_streak": {"en": "Streak bonus", "kn": "ನಿರಂತರತೆ ಬೋನಸ್", "hi": "स्ट्रीक बोनस"},
    "elig_prompt": {
        "en": "🩺 <b>Quick health check</b>\nBefore you go, do any of these apply to you?\n\n"
              "• Fever, cold, cough or infection in the last 2 weeks\n• Antibiotics in the last 7 days\n"
              "• Alcohol in the last 24 hours\n• Tattoo, piercing or acupuncture in the last 12 months\n"
              "• Surgery in the last 6 months\n• (Women) pregnant, delivered or breastfeeding in the last 12 months\n"
              "• Younger than 18, older than 65, or under 45 kg",
        "kn": "🩺 <b>ತ್ವರಿತ ಆರೋಗ್ಯ ಪರಿಶೀಲನೆ</b>\nಹೊರಡುವ ಮೊದಲು, ಇವುಗಳಲ್ಲಿ ಯಾವುದಾದರೂ ನಿಮಗೆ ಅನ್ವಯಿಸುತ್ತದೆಯೇ?\n\n"
              "• ಕಳೆದ 2 ವಾರಗಳಲ್ಲಿ ಜ್ವರ, ನೆಗಡಿ, ಕೆಮ್ಮು ಅಥವಾ ಸೋಂಕು\n• ಕಳೆದ 7 ದಿನಗಳಲ್ಲಿ ಆಂಟಿಬಯೋಟಿಕ್\n"
              "• ಕಳೆದ 24 ಗಂಟೆಗಳಲ್ಲಿ ಮದ್ಯಪಾನ\n• ಕಳೆದ 12 ತಿಂಗಳಲ್ಲಿ ಟ್ಯಾಟೂ, ಚುಚ್ಚುವಿಕೆ ಅಥವಾ ಅಕ್ಯುಪಂಕ್ಚರ್\n"
              "• ಕಳೆದ 6 ತಿಂಗಳಲ್ಲಿ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ\n• (ಮಹಿಳೆಯರು) ಕಳೆದ 12 ತಿಂಗಳಲ್ಲಿ ಗರ್ಭಿಣಿ, ಹೆರಿಗೆ ಅಥವಾ ಸ್ತನ್ಯಪಾನ\n"
              "• 18 ಕ್ಕಿಂತ ಕಡಿಮೆ, 65 ಕ್ಕಿಂತ ಹೆಚ್ಚು ವಯಸ್ಸು, ಅಥವಾ 45 ಕೆಜಿಗಿಂತ ಕಡಿಮೆ ತೂಕ",
        "hi": "🩺 <b>जल्दी स्वास्थ्य जाँच</b>\nनिकलने से पहले, क्या इनमें से कुछ भी आप पर लागू होता है?\n\n"
              "• पिछले 2 हफ़्तों में बुखार, सर्दी, खाँसी या संक्रमण\n• पिछले 7 दिनों में एंटीबायोटिक\n"
              "• पिछले 24 घंटों में शराब\n• पिछले 12 महीनों में टैटू, पियर्सिंग या एक्यूपंक्चर\n"
              "• पिछले 6 महीनों में सर्जरी\n• (महिलाएँ) पिछले 12 महीनों में गर्भावस्था, प्रसव या स्तनपान\n"
              "• उम्र 18 से कम या 65 से ज़्यादा, या वज़न 45 किलो से कम",
    },
    "login_ok": {"en": "✅ You're signed in on the website, {name}. You can go back to your browser.",
                 "kn": "✅ {name}, ನೀವು ವೆಬ್‌ಸೈಟ್‌ಗೆ ಸೈನ್ ಇನ್ ಆಗಿದ್ದೀರಿ. ಬ್ರೌಸರ್‌ಗೆ ಹಿಂತಿರುಗಬಹುದು.",
                 "hi": "✅ {name}, आप वेबसाइट पर साइन इन हो गए हैं। अब ब्राउज़र पर लौट सकते हैं।"},
    "login_expired": {"en": "⌛ This sign-in link has expired. Please try again on the website.",
                      "kn": "⌛ ಈ ಸೈನ್-ಇನ್ ಲಿಂಕ್ ಅವಧಿ ಮುಗಿದಿದೆ. ವೆಬ್‌ಸೈಟ್‌ನಲ್ಲಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
                      "hi": "⌛ इस साइन-इन लिंक की अवधि खत्म हो गई। वेबसाइट पर फिर से कोशिश करें।"},
    "link_taken": {"en": "⚠️ This Telegram account is already linked to {name}.",
                   "kn": "⚠️ ಈ ಟೆಲಿಗ್ರಾಮ್ ಖಾತೆ ಈಗಾಗಲೇ {name} ಅವರಿಗೆ ಜೋಡಿಸಲಾಗಿದೆ.",
                   "hi": "⚠️ यह टेलीग्राम अकाउंट पहले से {name} से जुड़ा है।"},
    "rem_later": {"en": "👍 No problem, we'll keep you posted.", "kn": "👍 ಪರವಾಗಿಲ್ಲ, ನಿಮಗೆ ತಿಳಿಸುತ್ತೇವೆ.",
                  "hi": "👍 कोई बात नहीं, हम आपको बताते रहेंगे।"},
    "elig_ok_btn": {"en": "✅ None apply — I'll donate", "kn": "✅ ಯಾವುದೂ ಅನ್ವಯಿಸದು — ದಾನ ಮಾಡುತ್ತೇನೆ",
                    "hi": "✅ कोई लागू नहीं — मैं दान करूँगा"},
    "elig_no_btn": {"en": "✋ One of these applies", "kn": "✋ ಇವುಗಳಲ್ಲಿ ಒಂದು ಅನ್ವಯಿಸುತ್ತದೆ", "hi": "✋ इनमें से कुछ लागू है"},
    "elig_deferred": {
        "en": "🙏 Thank you for being honest — that keeps donors and patients safe. Please don't donate today; "
              "you can set when you're able to again on your profile:\n{url}",
        "kn": "🙏 ಪ್ರಾಮಾಣಿಕತೆಗೆ ಧನ್ಯವಾದ — ಇದು ದಾನಿಗಳು ಮತ್ತು ರೋಗಿಗಳನ್ನು ಸುರಕ್ಷಿತವಾಗಿರಿಸುತ್ತದೆ. ದಯವಿಟ್ಟು ಇಂದು ದಾನ ಮಾಡಬೇಡಿ; "
              "ಮತ್ತೆ ಯಾವಾಗ ಸಾಧ್ಯ ಎಂಬುದನ್ನು ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನಲ್ಲಿ ನೋಡಿ:\n{url}",
        "hi": "🙏 ईमानदारी के लिए धन्यवाद — इससे डोनर और मरीज़ दोनों सुरक्षित रहते हैं। कृपया आज रक्तदान न करें; "
              "दोबारा कब कर सकते हैं, यह अपनी प्रोफ़ाइल पर देखें:\n{url}",
    },
    "elig_wait": {"en": "⏳ Not yet: you can donate again from {date}. Thank you for wanting to help!",
                  "kn": "⏳ ಇನ್ನೂ ಇಲ್ಲ: {date} ರಿಂದ ಮತ್ತೆ ದಾನ ಮಾಡಬಹುದು. ಸಹಾಯ ಮಾಡುವ ಮನಸ್ಸಿಗೆ ಧನ್ಯವಾದ!",
                  "hi": "⏳ अभी नहीं: आप {date} से फिर रक्तदान कर सकते हैं। मदद की इच्छा के लिए धन्यवाद!"},
    "elig_not_now": {"en": "⏳ You can't donate right now. See why on your profile: {url}",
                     "kn": "⏳ ಸದ್ಯಕ್ಕೆ ದಾನ ಮಾಡಲಾಗದು. ಕಾರಣ ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನಲ್ಲಿ ನೋಡಿ: {url}",
                     "hi": "⏳ आप अभी रक्तदान नहीं कर सकते। वजह अपनी प्रोफ़ाइल पर देखें: {url}"},
    "not_registered": {
        "en": "You're not registered yet. Tap below to join — it takes 20 seconds.",
        "kn": "ನೀವು ಇನ್ನೂ ನೋಂದಾಯಿಸಿಲ್ಲ. ಸೇರಲು ಕೆಳಗೆ ಒತ್ತಿ — 20 ಸೆಕೆಂಡು ಸಾಕು.",
        "hi": "आप अभी रजिस्टर्ड नहीं हैं। जुड़ने के लिए नीचे दबाएँ — सिर्फ़ 20 सेकंड।",
    },
    "lbl_donations": {"en": "Donations", "kn": "ರಕ್ತದಾನಗಳು", "hi": "रक्तदान"},
    "lbl_referrals": {"en": "Referrals", "kn": "ಆಹ್ವಾನಗಳು", "hi": "आमंत्रण"},
    "lbl_donated": {"en": "donated", "kn": "ದಾನ ಮಾಡಿದವರು", "hi": "दान किया"},
    "lbl_available": {"en": "🟢 Available to donate", "kn": "🟢 ದಾನಕ್ಕೆ ಲಭ್ಯ", "hi": "🟢 दान के लिए उपलब्ध"},
    "lbl_unavailable": {"en": "⚪ Not available", "kn": "⚪ ಲಭ್ಯವಿಲ್ಲ", "hi": "⚪ उपलब्ध नहीं"},
    "lbl_code": {"en": "Code", "kn": "ಕೋಡ್", "hi": "कोड"},
    "lbl_to_next": {"en": "{n} BLP to {badge}", "kn": "{badge} ಗೆ ಇನ್ನೂ {n} BLP", "hi": "{badge} तक {n} BLP बाकी"},
    "no_requests": {"en": "✨ No active requests right now.", "kn": "✨ ಸದ್ಯಕ್ಕೆ ಯಾವುದೇ ಸಕ್ರಿಯ ವಿನಂತಿಗಳಿಲ್ಲ.",
                    "hi": "✨ अभी कोई सक्रिय अनुरोध नहीं है।"},
    "no_requests_match": {
        "en": "✨ No active requests matching your blood group right now.",
        "kn": "✨ ನಿಮ್ಮ ರಕ್ತದ ಗುಂಪಿಗೆ ಹೊಂದುವ ಸಕ್ರಿಯ ವಿನಂತಿಗಳು ಸದ್ಯಕ್ಕೆ ಇಲ್ಲ.",
        "hi": "✨ अभी आपके ब्लड ग्रुप से मेल खाता कोई सक्रिय अनुरोध नहीं है।",
    },
    "btn_directions": {"en": "🗺️ Directions", "kn": "🗺️ ದಾರಿ", "hi": "🗺️ रास्ता"},
    "btn_uber": {"en": "🚕 Book Uber", "kn": "🚕 ಉಬರ್ ಬುಕ್ ಮಾಡಿ", "hi": "🚕 उबर बुक करें"},
    "btn_ride_help": {"en": "🆘 I need help getting there", "kn": "🆘 ಅಲ್ಲಿಗೆ ತಲುಪಲು ಸಹಾಯ ಬೇಕು",
                      "hi": "🆘 वहाँ पहुँचने में मदद चाहिए"},
    "ride_sent": {"en": "🆘 Help requested. The hospital or the family will call you on <b>{phone}</b> to arrange a pickup or a cab.",
                  "kn": "🆘 ಸಹಾಯ ಕೋರಲಾಗಿದೆ. ಕರೆದೊಯ್ಯಲು ಅಥವಾ ಕ್ಯಾಬ್ ವ್ಯವಸ್ಥೆಗೆ ಆಸ್ಪತ್ರೆ ಅಥವಾ ಕುಟುಂಬದವರು <b>{phone}</b> ಗೆ ಕರೆ ಮಾಡುತ್ತಾರೆ.",
                  "hi": "🆘 मदद माँगी गई। अस्पताल या परिवार लाने या कैब की व्यवस्था के लिए आपको <b>{phone}</b> पर कॉल करेंगे।"},
    "ride_sent_nophone": {"en": "🆘 Help requested. We don't have your phone number, so please call the contact number on the request too.",
                          "kn": "🆘 ಸಹಾಯ ಕೋರಲಾಗಿದೆ. ನಿಮ್ಮ ಫೋನ್ ಸಂಖ್ಯೆ ನಮ್ಮಲ್ಲಿಲ್ಲ, ದಯವಿಟ್ಟು ವಿನಂತಿಯಲ್ಲಿರುವ ಸಂಪರ್ಕ ಸಂಖ್ಯೆಗೂ ಕರೆ ಮಾಡಿ.",
                          "hi": "🆘 मदद माँगी गई। हमारे पास आपका फ़ोन नंबर नहीं है, इसलिए कृपया अनुरोध पर दिए नंबर पर भी कॉल करें।"},
    "ride_already": {"en": "You've already asked for help with this pledge. They'll contact you soon.",
                     "kn": "ಈ ವಾಗ್ದಾನಕ್ಕೆ ನೀವು ಈಗಾಗಲೇ ಸಹಾಯ ಕೋರಿದ್ದೀರಿ. ಅವರು ಶೀಘ್ರದಲ್ಲೇ ಸಂಪರ್ಕಿಸುತ್ತಾರೆ.",
                     "hi": "आप इस वादे के लिए पहले ही मदद माँग चुके हैं। वे जल्द ही संपर्क करेंगे।"},
    "req_km": {"en": "📍 About {km} km away", "kn": "📍 ಸುಮಾರು {km} ಕಿಮೀ ದೂರ", "hi": "📍 लगभग {km} किमी दूर"},
    "req_item": {
        "en": "🚨 <b>{group}</b> needed — {urgency}\n🏥 {hospital}, {city}\n🩸 {done}/{units} units · #{id}",
        "kn": "🚨 <b>{group}</b> ಬೇಕಾಗಿದೆ — {urgency}\n🏥 {hospital}, {city}\n🩸 {done}/{units} ಯೂನಿಟ್ · #{id}",
        "hi": "🚨 <b>{group}</b> चाहिए — {urgency}\n🏥 {hospital}, {city}\n🩸 {done}/{units} यूनिट · #{id}",
    },
    "register_to_respond": {"en": "Register to respond to requests.", "kn": "ವಿನಂತಿಗಳಿಗೆ ಪ್ರತಿಕ್ರಿಯಿಸಲು ನೋಂದಾಯಿಸಿ.",
                            "hi": "अनुरोधों का जवाब देने के लिए रजिस्टर करें।"},
    "avail_on": {"en": "🟢 You're <b>available</b> — you'll receive SOS alerts.",
                 "kn": "🟢 ನೀವು <b>ಲಭ್ಯ</b> — SOS ಎಚ್ಚರಿಕೆಗಳು ಬರುತ್ತವೆ.",
                 "hi": "🟢 आप <b>उपलब्ध</b> हैं — आपको SOS अलर्ट मिलेंगे।"},
    "avail_off": {"en": "⚪ Alerts <b>paused</b>. Tap “I'm available” to turn them back on.",
                  "kn": "⚪ ಎಚ್ಚರಿಕೆಗಳನ್ನು <b>ನಿಲ್ಲಿಸಲಾಗಿದೆ</b>. ಮತ್ತೆ ಆನ್ ಮಾಡಲು “ನಾನು ಲಭ್ಯವಿದ್ದೇನೆ” ಒತ್ತಿ.",
                  "hi": "⚪ अलर्ट <b>रोक दिए गए</b>। दोबारा चालू करने के लिए “मैं उपलब्ध हूँ” दबाएँ।"},
    "rewards": {"en": "🎁 <b>Rewards Store</b> (demo vouchers)", "kn": "🎁 <b>ಬಹುಮಾನ ಮಳಿಗೆ</b> (ಡೆಮೊ ವೋಚರ್‌ಗಳು)",
                "hi": "🎁 <b>इनाम स्टोर</b> (डेमो वाउचर)"},
    "balance": {"en": "Your balance: <b>{points} BLP</b>", "kn": "ನಿಮ್ಮ ಬ್ಯಾಲೆನ್ಸ್: <b>{points} BLP</b>",
                "hi": "आपका बैलेंस: <b>{points} BLP</b>"},
    "register_to_redeem": {"en": "Register to redeem rewards.", "kn": "ಬಹುಮಾನ ಪಡೆಯಲು ನೋಂದಾಯಿಸಿ.",
                           "hi": "इनाम पाने के लिए रजिस्टर करें।"},
    "redeemed_popup": {"en": "Redeemed! Your voucher code is in the chat 🎉", "kn": "ಪಡೆಯಲಾಗಿದೆ! ವೋಚರ್ ಕೋಡ್ ಚಾಟ್‌ನಲ್ಲಿದೆ 🎉",
                       "hi": "मिल गया! वाउचर कोड चैट में है 🎉"},
    "leaderboard": {"en": "🏆 <b>TOP HEROES</b>", "kn": "🏆 <b>ಅಗ್ರ ಹೀರೋಗಳು</b>", "hi": "🏆 <b>टॉप हीरो</b>"},
    "ach_title": {"en": "🏅 <b>YOUR ACHIEVEMENTS</b>", "kn": "🏅 <b>ನಿಮ್ಮ ಸಾಧನೆಗಳು</b>", "hi": "🏅 <b>आपकी उपलब्धियाँ</b>"},
    "ach_summary": {"en": "{unlocked}/{total} unlocked · +{points} BLP earned",
                    "kn": "{unlocked}/{total} ಅನ್‌ಲಾಕ್ · +{points} BLP ಗಳಿಸಲಾಗಿದೆ",
                    "hi": "{unlocked}/{total} अनलॉक · +{points} BLP कमाए"},
    "ach_tiers": {"en": "<b>Tiered badges</b>", "kn": "<b>ಹಂತದ ಬ್ಯಾಡ್ಜ್‌ಗಳು</b>", "hi": "<b>स्तर वाले बैज</b>"},
    "ach_recent": {"en": "<b>Latest unlocks</b>", "kn": "<b>ಇತ್ತೀಚಿನ ಸಾಧನೆಗಳು</b>", "hi": "<b>हाल की उपलब्धियाँ</b>"},
    "ach_next": {"en": "<b>Up next</b>", "kn": "<b>ಮುಂದಿನ ಗುರಿ</b>", "hi": "<b>अगला लक्ष्य</b>"},
    "ach_none": {"en": "No achievements yet. Your first donation unlocks 🩸 First Drop!",
                 "kn": "ಇನ್ನೂ ಸಾಧನೆಗಳಿಲ್ಲ. ಮೊದಲ ರಕ್ತದಾನ 🩸 First Drop ಅನ್‌ಲಾಕ್ ಮಾಡುತ್ತದೆ!",
                 "hi": "अभी कोई उपलब्धि नहीं। पहला रक्तदान 🩸 First Drop अनलॉक करेगा!"},
    "ach_locked": {"en": "locked", "kn": "ಲಾಕ್", "hi": "लॉक"},
    "cancelled": {"en": "Cancelled.", "kn": "ರದ್ದುಗೊಳಿಸಲಾಗಿದೆ.", "hi": "रद्द किया गया।"},
    "unknown": {"en": "Tap a button below 👇", "kn": "ಕೆಳಗಿನ ಬಟನ್ ಒತ್ತಿ 👇", "hi": "नीचे दिया बटन दबाएँ 👇"},
    "error": {"en": "⚠️ Something went wrong. Please try again.", "kn": "⚠️ ಏನೋ ತಪ್ಪಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
              "hi": "⚠️ कुछ गड़बड़ हो गई। कृपया फिर से कोशिश करें।"},
    "server_down": {
        "en": "⚠️ BloodLink server is unreachable right now. Please try again shortly.",
        "kn": "⚠️ BloodLink ಸರ್ವರ್ ಸದ್ಯಕ್ಕೆ ಲಭ್ಯವಿಲ್ಲ. ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಪ್ರಯತ್ನಿಸಿ.",
        "hi": "⚠️ BloodLink सर्वर अभी उपलब्ध नहीं है। थोड़ी देर बाद कोशिश करें।",
    },
}

# Telegram "/" command menu descriptions per language
COMMANDS = {
    "en": [("menu", "🏠 Main menu"), ("sos", "🚨 Request blood"), ("register", "🩸 Become a donor"),
           ("requests", "📋 Active requests"), ("me", "👤 My profile"), ("achievements", "🏅 Achievements"), ("camps", "🏕️ Donation camps"), ("teams", "👥 My teams"), ("language", "🌐 Change language")],
    "kn": [("menu", "🏠 ಮುಖ್ಯ ಮೆನು"), ("sos", "🚨 ರಕ್ತ ವಿನಂತಿ"), ("register", "🩸 ದಾನಿಯಾಗಿ"),
           ("requests", "📋 ಸಕ್ರಿಯ ವಿನಂತಿಗಳು"), ("me", "👤 ನನ್ನ ಪ್ರೊಫೈಲ್"), ("achievements", "🏅 ಸಾಧನೆಗಳು"), ("language", "🌐 ಭಾಷೆ ಬದಲಿಸಿ")],
    "hi": [("menu", "🏠 मुख्य मेनू"), ("sos", "🚨 खून का अनुरोध"), ("register", "🩸 डोनर बनें"),
           ("requests", "📋 सक्रिय अनुरोध"), ("me", "👤 मेरी प्रोफ़ाइल"), ("achievements", "🏅 उपलब्धियाँ"), ("language", "🌐 भाषा बदलें")],
}


def t(lang: str | None, key: str, **kwargs) -> str:
    entry = S[key]
    return entry.get(lang or "en", entry["en"]).format(**kwargs)


# Sanity check at import: every key has every language
for _k, _v in S.items():
    assert set(_v) == set(LANGS), f"i18n key {_k!r} is missing a language"

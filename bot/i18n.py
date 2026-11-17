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
    "donated": {
        "en": "✅ <b>You're donating for request #{id}</b>\n🏥 {hospital}, {city} — {group}{phone}\n\n"
              "🎉 <b>Thank you! You earned {points} BLP!</b>\n{lines}\n\nBalance: <b>{balance} BLP</b> · {badge}\n"
              "Please carry a photo ID to the hospital.",
        "kn": "✅ <b>ವಿನಂತಿ #{id} ಗಾಗಿ ನೀವು ರಕ್ತದಾನ ಮಾಡುತ್ತಿದ್ದೀರಿ</b>\n🏥 {hospital}, {city} — {group}{phone}\n\n"
              "🎉 <b>ಧನ್ಯವಾದಗಳು! ನೀವು {points} BLP ಗಳಿಸಿದ್ದೀರಿ!</b>\n{lines}\n\nಬ್ಯಾಲೆನ್ಸ್: <b>{balance} BLP</b> · {badge}\n"
              "ದಯವಿಟ್ಟು ಆಸ್ಪತ್ರೆಗೆ ಫೋಟೋ ಐಡಿ ತನ್ನಿ.",
        "hi": "✅ <b>आप अनुरोध #{id} के लिए रक्तदान कर रहे हैं</b>\n🏥 {hospital}, {city} — {group}{phone}\n\n"
              "🎉 <b>धन्यवाद! आपने {points} BLP कमाए!</b>\n{lines}\n\nबैलेंस: <b>{balance} BLP</b> · {badge}\n"
              "कृपया अस्पताल में फ़ोटो पहचान पत्र साथ लाएँ।",
    },
    "contact": {"en": "\n📞 Contact: {phone}", "kn": "\n📞 ಸಂಪರ್ಕ: {phone}", "hi": "\n📞 संपर्क: {phone}"},
    "bd_donation": {"en": "Successful donation", "kn": "ಯಶಸ್ವಿ ರಕ್ತದಾನ", "hi": "सफल रक्तदान"},
    "bd_quick": {"en": "Quick response (< 5 min)", "kn": "ತ್ವರಿತ ಪ್ರತಿಕ್ರಿಯೆ (< 5 ನಿಮಿಷ)", "hi": "तेज़ जवाब (< 5 मिनट)"},
    "bd_streak": {"en": "Streak bonus", "kn": "ನಿರಂತರತೆ ಬೋನಸ್", "hi": "स्ट्रीक बोनस"},
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
           ("requests", "📋 Active requests"), ("me", "👤 My profile"), ("language", "🌐 Change language")],
    "kn": [("menu", "🏠 ಮುಖ್ಯ ಮೆನು"), ("sos", "🚨 ರಕ್ತ ವಿನಂತಿ"), ("register", "🩸 ದಾನಿಯಾಗಿ"),
           ("requests", "📋 ಸಕ್ರಿಯ ವಿನಂತಿಗಳು"), ("me", "👤 ನನ್ನ ಪ್ರೊಫೈಲ್"), ("language", "🌐 ಭಾಷೆ ಬದಲಿಸಿ")],
    "hi": [("menu", "🏠 मुख्य मेनू"), ("sos", "🚨 खून का अनुरोध"), ("register", "🩸 डोनर बनें"),
           ("requests", "📋 सक्रिय अनुरोध"), ("me", "👤 मेरी प्रोफ़ाइल"), ("language", "🌐 भाषा बदलें")],
}


def t(lang: str | None, key: str, **kwargs) -> str:
    entry = S[key]
    return entry.get(lang or "en", entry["en"]).format(**kwargs)


# Sanity check at import: every key has every language
for _k, _v in S.items():
    assert set(_v) == set(LANGS), f"i18n key {_k!r} is missing a language"

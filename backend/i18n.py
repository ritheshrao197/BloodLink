"""Translations for messages the backend sends to Telegram (the bot has its own, larger table)."""

LANGUAGES = ("en", "kn", "hi")

STRINGS = {
    "en": {
        "rem_soon": "🩸 In {days} day(s) you can donate blood again. Get ready: eat well and stay hydrated!",
        "rem_where": " Your last donation at <b>{hospital}</b> helped save a life.",
        "rem_eligible": "🎉 <b>You're eligible to donate again!</b>{where}\n\nReady to be someone's hero today?",
        "rem_nudge": "💭 Still thinking about it? Patients near you are waiting. Turn on alerts whenever you're ready.",
        "rem_available_btn": "✅ I'm available",
        "rem_later_btn": "⏰ Later",
        "achievements": "🎉 <b>ACHIEVEMENT UNLOCKED!</b>\n\n{lines}\n\n💰 +{points} BLP awarded\n🏆 See your collection: /achievements",
        "sos_alert": "🚨 <b>EMERGENCY: {group} BLOOD NEEDED</b>\n\n🏥 {hospital}, {city}\n🩸 Units needed: {units}\n"
                     "{uicon} Urgency: {urgency}\n👤 Requested by: {name}\n\n"
                     "You are a compatible donor. Respond within 5 minutes for a +20 BLP quick-response bonus!",
        "donate_btn": "🩸 I Can Donate",
        "urg_Critical": "Critical", "urg_High": "Today", "urg_Normal": "Planned",
        "donor_coming": "✅ <b>{name}</b> ({group}) is coming to donate for your request at {hospital}.{contact}\n"
                        "Units: {done}/{units} — status: {status}",
        "contact": "\n📞 Donor contact: {phone}",
        "st_Active": "Active", "st_Fulfilled": "Fulfilled ✅",
        "ref_joined": "🎉 {name} joined BloodLink with your link! +{points} BLP",
        "ref_donated": "🩸 Your friend {name} just donated blood!\n+{points} BLP and a voucher: <code>{code}</code>",
        "redeemed": "🎁 You redeemed <b>{reward}</b>!\nVoucher code: <code>{code}</code>\n(Demo voucher — not redeemable)",
    },
    "kn": {
        "rem_soon": "🩸 ಇನ್ನು {days} ದಿನಗಳಲ್ಲಿ ನೀವು ಮತ್ತೆ ರಕ್ತದಾನ ಮಾಡಬಹುದು. ಚೆನ್ನಾಗಿ ತಿನ್ನಿ, ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ!",
        "rem_where": " <b>{hospital}</b> ನಲ್ಲಿ ನಿಮ್ಮ ಕೊನೆಯ ದಾನ ಒಂದು ಜೀವ ಉಳಿಸಲು ಸಹಾಯ ಮಾಡಿತು.",
        "rem_eligible": "🎉 <b>ನೀವು ಮತ್ತೆ ರಕ್ತದಾನ ಮಾಡಬಹುದು!</b>{where}\n\nಇಂದು ಯಾರಿಗಾದರೂ ವೀರರಾಗಲು ಸಿದ್ಧರೇ?",
        "rem_nudge": "💭 ಇನ್ನೂ ಯೋಚಿಸುತ್ತಿದ್ದೀರಾ? ನಿಮ್ಮ ಹತ್ತಿರದ ರೋಗಿಗಳು ಕಾಯುತ್ತಿದ್ದಾರೆ. ಸಿದ್ಧರಾದಾಗ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಆನ್ ಮಾಡಿ.",
        "rem_available_btn": "✅ ನಾನು ಲಭ್ಯ",
        "rem_later_btn": "⏰ ನಂತರ",
        "achievements": "🎉 <b>ಸಾಧನೆ ಅನ್‌ಲಾಕ್ ಆಗಿದೆ!</b>\n\n{lines}\n\n💰 +{points} BLP ನೀಡಲಾಗಿದೆ\n🏆 ನಿಮ್ಮ ಸಂಗ್ರಹ: /achievements",
        "sos_alert": "🚨 <b>ತುರ್ತು: {group} ರಕ್ತ ಬೇಕಾಗಿದೆ</b>\n\n🏥 {hospital}, {city}\n🩸 ಬೇಕಾದ ಯೂನಿಟ್: {units}\n"
                     "{uicon} ತುರ್ತು ಮಟ್ಟ: {urgency}\n👤 ವಿನಂತಿಸಿದವರು: {name}\n\n"
                     "ನೀವು ಹೊಂದಾಣಿಕೆಯ ದಾನಿ. 5 ನಿಮಿಷದೊಳಗೆ ಪ್ರತಿಕ್ರಿಯಿಸಿದರೆ +20 BLP ಬೋನಸ್!",
        "donate_btn": "🩸 ನಾನು ದಾನ ಮಾಡಬಲ್ಲೆ",
        "urg_Critical": "ಅತಿ ತುರ್ತು", "urg_High": "ಇಂದೇ", "urg_Normal": "ಯೋಜಿತ",
        "donor_coming": "✅ <b>{name}</b> ({group}) {hospital} ನಲ್ಲಿ ನಿಮ್ಮ ವಿನಂತಿಗೆ ರಕ್ತದಾನ ಮಾಡಲು ಬರುತ್ತಿದ್ದಾರೆ.{contact}\n"
                        "ಯೂನಿಟ್: {done}/{units} — ಸ್ಥಿತಿ: {status}",
        "contact": "\n📞 ದಾನಿಯ ಸಂಪರ್ಕ: {phone}",
        "st_Active": "ಸಕ್ರಿಯ", "st_Fulfilled": "ಪೂರ್ಣಗೊಂಡಿದೆ ✅",
        "ref_joined": "🎉 {name} ನಿಮ್ಮ ಲಿಂಕ್ ಮೂಲಕ BloodLink ಸೇರಿದ್ದಾರೆ! +{points} BLP",
        "ref_donated": "🩸 ನಿಮ್ಮ ಸ್ನೇಹಿತ {name} ಈಗಷ್ಟೇ ರಕ್ತದಾನ ಮಾಡಿದ್ದಾರೆ!\n+{points} BLP ಮತ್ತು ವೋಚರ್: <code>{code}</code>",
        "redeemed": "🎁 ನೀವು <b>{reward}</b> ಪಡೆದಿದ್ದೀರಿ!\nವೋಚರ್ ಕೋಡ್: <code>{code}</code>\n(ಡೆಮೊ ವೋಚರ್)",
    },
    "hi": {
        "rem_soon": "🩸 {days} दिन बाद आप फिर रक्तदान कर सकते हैं। तैयार रहें: अच्छा खाएँ और खूब पानी पिएँ!",
        "rem_where": " <b>{hospital}</b> में आपके पिछले रक्तदान ने एक जान बचाने में मदद की।",
        "rem_eligible": "🎉 <b>आप फिर से रक्तदान कर सकते हैं!</b>{where}\n\nआज किसी के हीरो बनने के लिए तैयार हैं?",
        "rem_nudge": "💭 अभी सोच रहे हैं? आपके पास के मरीज़ इंतज़ार कर रहे हैं। जब तैयार हों, अलर्ट चालू करें।",
        "rem_available_btn": "✅ मैं उपलब्ध हूँ",
        "rem_later_btn": "⏰ बाद में",
        "achievements": "🎉 <b>उपलब्धि अनलॉक!</b>\n\n{lines}\n\n💰 +{points} BLP मिले\n🏆 अपना संग्रह देखें: /achievements",
        "sos_alert": "🚨 <b>आपातकाल: {group} खून चाहिए</b>\n\n🏥 {hospital}, {city}\n🩸 ज़रूरी यूनिट: {units}\n"
                     "{uicon} तात्कालिकता: {urgency}\n👤 अनुरोधकर्ता: {name}\n\n"
                     "आप मेल खाते डोनर हैं। 5 मिनट में जवाब दें और +20 BLP बोनस पाएँ!",
        "donate_btn": "🩸 मैं रक्तदान करूँगा/करूँगी",
        "urg_Critical": "बहुत ज़रूरी", "urg_High": "आज ही", "urg_Normal": "तय ऑपरेशन",
        "donor_coming": "✅ <b>{name}</b> ({group}) {hospital} में आपके अनुरोध के लिए रक्तदान करने आ रहे हैं।{contact}\n"
                        "यूनिट: {done}/{units} — स्थिति: {status}",
        "contact": "\n📞 डोनर का संपर्क: {phone}",
        "st_Active": "सक्रिय", "st_Fulfilled": "पूरा हुआ ✅",
        "ref_joined": "🎉 {name} आपके लिंक से BloodLink से जुड़े! +{points} BLP",
        "ref_donated": "🩸 आपके दोस्त {name} ने अभी रक्तदान किया!\n+{points} BLP और वाउचर: <code>{code}</code>",
        "redeemed": "🎁 आपने <b>{reward}</b> लिया!\nवाउचर कोड: <code>{code}</code>\n(डेमो वाउचर)",
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    table = STRINGS.get(lang or "en", STRINGS["en"])
    return table.get(key, STRINGS["en"][key]).format(**kwargs)

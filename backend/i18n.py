"""Translations for messages the backend sends to Telegram (the bot has its own, larger table)."""

LANGUAGES = ("en", "kn", "hi")

STRINGS = {
    "en": {
        "dist": "📍 About {km} km from you",
        "camp_rsvp": "✅ You're registered for <b>{title}</b>!\n📍 {venue}\n🗓 {when}\nWe'll remind you before the day.",
        "camp_thanks": "🎉 Thank you for donating at <b>{title}</b>! +{points} BLP. Your next donation date is on your profile.",
        "rem_camp3": "📅 <b>{title}</b> is in 3 days ({when}) at {venue}. Still coming? Eat well and sleep well before it.",
        "rem_camp1": "🚨 Tomorrow: <b>{title}</b> at {venue}, {when}. Eat a proper meal and drink plenty of water.",
        "rem_camp0": "🩸 It's today! <b>{title}</b> at {venue}, {when}. Bring a photo ID. Thank you, hero!",
        "rem_soon": "🩸 In {days} day(s) you can donate blood again. Get ready: eat well and stay hydrated!",
        "rem_where": " Your last donation at <b>{hospital}</b> helped save a life.",
        "rem_eligible": "🎉 <b>You're eligible to donate again!</b>{where}\n\nReady to be someone's hero today?",
        "rem_nudge": "💭 Still thinking about it? Patients near you are waiting. Turn on alerts whenever you're ready.",
        "rem_available_btn": "✅ I'm available",
        "rem_later_btn": "⏰ Later",
        "achievements": "🎉 <b>ACHIEVEMENT UNLOCKED!</b>\n\n{lines}\n\n💰 +{points} BLP awarded\n🏆 See your collection: /achievements",
        "sos_alert": "🚨 <b>EMERGENCY: {group} BLOOD NEEDED</b>\n\n🏥 {hospital}, {city}\n🩸 Units needed: {units}\n"
                     "{uicon} Urgency: {urgency}\n👤 Requested by: {name}\n\n"
                     "You are a compatible donor. Quick responders get a +20 BLP bonus once the hospital confirms the donation.",
        "donate_btn": "🩸 I Can Donate",
        "urg_Critical": "Critical", "urg_High": "Today", "urg_Normal": "Planned",
        "donor_coming": "✅ <b>{name}</b> ({group}) is coming to donate for your request at {hospital}.{contact}\n"
                        "Units: {done}/{units} — status: {status}",
        "contact": "\n📞 Donor contact: {phone}",
        "st_Active": "Active", "st_Fulfilled": "Fulfilled ✅",
        "ref_joined": "🎉 {name} joined BloodLink with your link! +{points} BLP",
        "staff_pledge": "🩸 <b>Donor on the way</b> for request #{id}\n👤 {name} ({group}){phone}\n🏥 {hospital}, {city}\n\n"
                        "Tap <b>Donated</b> once they have donated, or <b>Didn't come</b>. Unconfirmed pledges expire in {hours} h.",
        "staff_done_btn": "✅ Donated",
        "staff_noshow_btn": "❌ Didn't come",
        "pledge_confirmed": "✅ <b>Donation confirmed</b> at {hospital}. Thank you!\n+{points} BLP · balance {balance} BLP\n"
                            "Your next donation date: <b>{next}</b>",
        "pledge_missed": "We couldn't confirm your donation at {hospital}, so no points were added. If you did donate, "
                         "please ask the hospital to confirm it.{blocked}",
        "pledge_blocked": "\nAfter {n} unconfirmed pledges, new pledges are paused until {until}.",
        "staff_lowhb_btn": "🩸 Low Hb",
        "hb_after": "🩸 Your haemoglobin: <b>{hb} g/dL</b> {mark}\nToday: drink extra fluids and skip heavy exercise. This week: eat iron-rich food (greens, dal, jaggery, eggs or meat).",
        "hb_low": "💙 <b>You couldn't donate today: your haemoglobin was low.</b>\n{reading}\n\nThis is common and usually improves with food. Try:\n• green leafy vegetables, dal and other pulses\n• jaggery, dates, raisins and pomegranate\n• eggs, fish or meat if you eat them\n• something with vitamin C (lemon, amla, orange) with meals, and less tea or coffee around meals\n\nIf this happens again, please see a doctor. You can try donating again from <b>{until}</b>.",
        "hb_low_value": "Your reading was {hb} g/dL; the minimum to donate is 12.5 g/dL.",
        "hb_low_novalue": "It was below the 12.5 g/dL minimum needed to donate.",
        "rem_iron": "\n🍽️ Tip: eat iron-rich food (greens, dal, jaggery, eggs or meat) this week so your haemoglobin passes the check.",
        "rem_iron_borderline": "\n🍽️ Your last haemoglobin was {hb} g/dL, close to the 12.5 minimum. Eat iron-rich food every day this week (greens, dal, jaggery, dates, eggs or meat) with some lemon or amla.",
        "ride_help": "🆘 <b>{name}</b> ({group}) pledged for request #{id} at {hospital} and <b>needs help getting there</b>.\n📍 From {area}{phone}\nPlease call them to arrange a pickup or a cab.",
        "ref_donated": "🩸 Your friend {name} just donated blood!\n+{points} BLP and a voucher: <code>{code}</code>",
        "redeemed": "🎁 You redeemed <b>{reward}</b>!\nVoucher code: <code>{code}</code>\n(Demo voucher — not redeemable)",
    },
    "kn": {
        "dist": "📍 ನಿಮ್ಮಿಂದ ಸುಮಾರು {km} ಕಿಮೀ ದೂರ",
        "camp_rsvp": "✅ <b>{title}</b> ಗೆ ನೋಂದಣಿ ಆಯಿತು!\n📍 {venue}\n🗓 {when}\nಹಿಂದಿನ ದಿನ ನೆನಪಿಸುತ್ತೇವೆ.",
        "camp_thanks": "🎉 <b>{title}</b> ನಲ್ಲಿ ರಕ್ತದಾನ ಮಾಡಿದ್ದಕ್ಕೆ ಧನ್ಯವಾದ! +{points} BLP. ಮುಂದಿನ ದಾನದ ದಿನಾಂಕ ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನಲ್ಲಿದೆ.",
        "rem_camp3": "📅 <b>{title}</b> ಇನ್ನು 3 ದಿನದಲ್ಲಿ ({when}), {venue} ನಲ್ಲಿ. ಬರುತ್ತೀರಲ್ಲವೇ? ಚೆನ್ನಾಗಿ ತಿನ್ನಿ, ಚೆನ್ನಾಗಿ ನಿದ್ರಿಸಿ.",
        "rem_camp1": "🚨 ನಾಳೆ: <b>{title}</b>, {venue}, {when}. ಸರಿಯಾಗಿ ಊಟ ಮಾಡಿ, ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ.",
        "rem_camp0": "🩸 ಇಂದೇ! <b>{title}</b>, {venue}, {when}. ಫೋಟೋ ಗುರುತಿನ ಚೀಟಿ ತನ್ನಿ. ಧನ್ಯವಾದ, ವೀರರೇ!",
        "rem_soon": "🩸 ಇನ್ನು {days} ದಿನಗಳಲ್ಲಿ ನೀವು ಮತ್ತೆ ರಕ್ತದಾನ ಮಾಡಬಹುದು. ಚೆನ್ನಾಗಿ ತಿನ್ನಿ, ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ!",
        "rem_where": " <b>{hospital}</b> ನಲ್ಲಿ ನಿಮ್ಮ ಕೊನೆಯ ದಾನ ಒಂದು ಜೀವ ಉಳಿಸಲು ಸಹಾಯ ಮಾಡಿತು.",
        "rem_eligible": "🎉 <b>ನೀವು ಮತ್ತೆ ರಕ್ತದಾನ ಮಾಡಬಹುದು!</b>{where}\n\nಇಂದು ಯಾರಿಗಾದರೂ ವೀರರಾಗಲು ಸಿದ್ಧರೇ?",
        "rem_nudge": "💭 ಇನ್ನೂ ಯೋಚಿಸುತ್ತಿದ್ದೀರಾ? ನಿಮ್ಮ ಹತ್ತಿರದ ರೋಗಿಗಳು ಕಾಯುತ್ತಿದ್ದಾರೆ. ಸಿದ್ಧರಾದಾಗ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಆನ್ ಮಾಡಿ.",
        "rem_available_btn": "✅ ನಾನು ಲಭ್ಯ",
        "rem_later_btn": "⏰ ನಂತರ",
        "achievements": "🎉 <b>ಸಾಧನೆ ಅನ್‌ಲಾಕ್ ಆಗಿದೆ!</b>\n\n{lines}\n\n💰 +{points} BLP ನೀಡಲಾಗಿದೆ\n🏆 ನಿಮ್ಮ ಸಂಗ್ರಹ: /achievements",
        "sos_alert": "🚨 <b>ತುರ್ತು: {group} ರಕ್ತ ಬೇಕಾಗಿದೆ</b>\n\n🏥 {hospital}, {city}\n🩸 ಬೇಕಾದ ಯೂನಿಟ್: {units}\n"
                     "{uicon} ತುರ್ತು ಮಟ್ಟ: {urgency}\n👤 ವಿನಂತಿಸಿದವರು: {name}\n\n"
                     "ನೀವು ಹೊಂದಾಣಿಕೆಯ ದಾನಿ. ಆಸ್ಪತ್ರೆ ರಕ್ತದಾನವನ್ನು ದೃಢೀಕರಿಸಿದ ನಂತರ ತ್ವರಿತವಾಗಿ ಪ್ರತಿಕ್ರಿಯಿಸಿದವರಿಗೆ +20 BLP ಬೋನಸ್.",
        "donate_btn": "🩸 ನಾನು ದಾನ ಮಾಡಬಲ್ಲೆ",
        "urg_Critical": "ಅತಿ ತುರ್ತು", "urg_High": "ಇಂದೇ", "urg_Normal": "ಯೋಜಿತ",
        "donor_coming": "✅ <b>{name}</b> ({group}) {hospital} ನಲ್ಲಿ ನಿಮ್ಮ ವಿನಂತಿಗೆ ರಕ್ತದಾನ ಮಾಡಲು ಬರುತ್ತಿದ್ದಾರೆ.{contact}\n"
                        "ಯೂನಿಟ್: {done}/{units} — ಸ್ಥಿತಿ: {status}",
        "contact": "\n📞 ದಾನಿಯ ಸಂಪರ್ಕ: {phone}",
        "st_Active": "ಸಕ್ರಿಯ", "st_Fulfilled": "ಪೂರ್ಣಗೊಂಡಿದೆ ✅",
        "ref_joined": "🎉 {name} ನಿಮ್ಮ ಲಿಂಕ್ ಮೂಲಕ BloodLink ಸೇರಿದ್ದಾರೆ! +{points} BLP",
        "staff_pledge": "🩸 ವಿನಂತಿ #{id} ಗೆ <b>ದಾನಿ ಬರುತ್ತಿದ್ದಾರೆ</b>\n👤 {name} ({group}){phone}\n🏥 {hospital}, {city}\n\n"
                        "ಅವರು ರಕ್ತದಾನ ಮಾಡಿದ ನಂತರ <b>ದಾನ ಮಾಡಿದರು</b> ಒತ್ತಿ, ಇಲ್ಲವೇ <b>ಬರಲಿಲ್ಲ</b>. ದೃಢೀಕರಿಸದ ವಾಗ್ದಾನಗಳು {hours} ಗಂಟೆಯಲ್ಲಿ ಮುಗಿಯುತ್ತವೆ.",
        "staff_done_btn": "✅ ದಾನ ಮಾಡಿದರು",
        "staff_noshow_btn": "❌ ಬರಲಿಲ್ಲ",
        "pledge_confirmed": "✅ {hospital} ನಲ್ಲಿ ನಿಮ್ಮ <b>ರಕ್ತದಾನ ದೃಢೀಕರಿಸಲಾಗಿದೆ</b>. ಧನ್ಯವಾದಗಳು!\n+{points} BLP · ಬ್ಯಾಲೆನ್ಸ್ {balance} BLP\n"
                            "ನಿಮ್ಮ ಮುಂದಿನ ರಕ್ತದಾನ ದಿನಾಂಕ: <b>{next}</b>",
        "pledge_missed": "{hospital} ನಲ್ಲಿ ನಿಮ್ಮ ರಕ್ತದಾನವನ್ನು ದೃಢೀಕರಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ, ಆದ್ದರಿಂದ ಅಂಕಗಳನ್ನು ಸೇರಿಸಲಾಗಿಲ್ಲ. "
                         "ನೀವು ದಾನ ಮಾಡಿದ್ದರೆ, ದಯವಿಟ್ಟು ಆಸ್ಪತ್ರೆಗೆ ದೃಢೀಕರಿಸಲು ಹೇಳಿ.{blocked}",
        "pledge_blocked": "\n{n} ದೃಢೀಕರಿಸದ ವಾಗ್ದಾನಗಳ ನಂತರ, ಹೊಸ ವಾಗ್ದಾನಗಳನ್ನು {until} ವರೆಗೆ ನಿಲ್ಲಿಸಲಾಗಿದೆ.",
        "staff_lowhb_btn": "🩸 ಕಡಿಮೆ Hb",
        "hb_after": "🩸 ನಿಮ್ಮ ಹಿಮೋಗ್ಲೋಬಿನ್: <b>{hb} g/dL</b> {mark}\nಇಂದು: ಹೆಚ್ಚು ನೀರು ಕುಡಿಯಿರಿ, ಭಾರೀ ವ್ಯಾಯಾಮ ಬೇಡ. ಈ ವಾರ: ಕಬ್ಬಿಣಾಂಶದ ಆಹಾರ ತಿನ್ನಿ (ಸೊಪ್ಪು, ಬೇಳೆ, ಬೆಲ್ಲ, ಮೊಟ್ಟೆ ಅಥವಾ ಮಾಂಸ).",
        "hb_low": "💙 <b>ಇಂದು ರಕ್ತದಾನ ಸಾಧ್ಯವಾಗಲಿಲ್ಲ: ನಿಮ್ಮ ಹಿಮೋಗ್ಲೋಬಿನ್ ಕಡಿಮೆ ಇತ್ತು.</b>\n{reading}\n\nಇದು ಸಾಮಾನ್ಯ, ಆಹಾರದಿಂದ ಸಾಮಾನ್ಯವಾಗಿ ಸುಧಾರಿಸುತ್ತದೆ. ಪ್ರಯತ್ನಿಸಿ:\n• ಹಸಿರು ಸೊಪ್ಪು, ಬೇಳೆ ಮತ್ತು ಇತರ ಕಾಳುಗಳು\n• ಬೆಲ್ಲ, ಖರ್ಜೂರ, ಒಣದ್ರಾಕ್ಷಿ ಮತ್ತು ದಾಳಿಂಬೆ\n• ನೀವು ತಿನ್ನುವಿರಾದರೆ ಮೊಟ್ಟೆ, ಮೀನು ಅಥವಾ ಮಾಂಸ\n• ಊಟದೊಂದಿಗೆ ವಿಟಮಿನ್ ಸಿ (ನಿಂಬೆ, ನೆಲ್ಲಿಕಾಯಿ, ಕಿತ್ತಳೆ), ಊಟದ ಸಮಯದಲ್ಲಿ ಕಡಿಮೆ ಚಹಾ ಅಥವಾ ಕಾಫಿ\n\nಮತ್ತೆ ಹೀಗಾದರೆ ದಯವಿಟ್ಟು ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ. <b>{until}</b> ರಿಂದ ಮತ್ತೆ ರಕ್ತದಾನಕ್ಕೆ ಪ್ರಯತ್ನಿಸಬಹುದು.",
        "hb_low_value": "ನಿಮ್ಮ ಅಳತೆ {hb} g/dL; ರಕ್ತದಾನಕ್ಕೆ ಕನಿಷ್ಠ 12.5 g/dL ಬೇಕು.",
        "hb_low_novalue": "ಇದು ರಕ್ತದಾನಕ್ಕೆ ಬೇಕಾದ ಕನಿಷ್ಠ 12.5 g/dL ಗಿಂತ ಕಡಿಮೆ ಇತ್ತು.",
        "rem_iron": "\n🍽️ ಸಲಹೆ: ನಿಮ್ಮ ಹಿಮೋಗ್ಲೋಬಿನ್ ಪರೀಕ್ಷೆ ಪಾಸಾಗಲು ಈ ವಾರ ಕಬ್ಬಿಣಾಂಶದ ಆಹಾರ ತಿನ್ನಿ (ಸೊಪ್ಪು, ಬೇಳೆ, ಬೆಲ್ಲ, ಮೊಟ್ಟೆ ಅಥವಾ ಮಾಂಸ).",
        "rem_iron_borderline": "\n🍽️ ನಿಮ್ಮ ಕೊನೆಯ ಹಿಮೋಗ್ಲೋಬಿನ್ {hb} g/dL, ಕನಿಷ್ಠ 12.5 ಕ್ಕೆ ಹತ್ತಿರ. ಈ ವಾರ ಪ್ರತಿದಿನ ಕಬ್ಬಿಣಾಂಶದ ಆಹಾರ ತಿನ್ನಿ (ಸೊಪ್ಪು, ಬೇಳೆ, ಬೆಲ್ಲ, ಖರ್ಜೂರ, ಮೊಟ್ಟೆ ಅಥವಾ ಮಾಂಸ), ಸ್ವಲ್ಪ ನಿಂಬೆ ಅಥವಾ ನೆಲ್ಲಿಕಾಯಿಯೊಂದಿಗೆ.",
        "ride_help": "🆘 <b>{name}</b> ({group}) {hospital} ನಲ್ಲಿ ವಿನಂತಿ #{id} ಗೆ ವಾಗ್ದಾನ ಮಾಡಿದ್ದಾರೆ ಮತ್ತು <b>ಅಲ್ಲಿಗೆ ತಲುಪಲು ಸಹಾಯ ಬೇಕು</b>.\n📍 {area} ನಿಂದ{phone}\nದಯವಿಟ್ಟು ಅವರಿಗೆ ಕರೆ ಮಾಡಿ, ಕರೆದೊಯ್ಯಲು ಅಥವಾ ಕ್ಯಾಬ್ ವ್ಯವಸ್ಥೆ ಮಾಡಿ.",
        "ref_donated": "🩸 ನಿಮ್ಮ ಸ್ನೇಹಿತ {name} ಈಗಷ್ಟೇ ರಕ್ತದಾನ ಮಾಡಿದ್ದಾರೆ!\n+{points} BLP ಮತ್ತು ವೋಚರ್: <code>{code}</code>",
        "redeemed": "🎁 ನೀವು <b>{reward}</b> ಪಡೆದಿದ್ದೀರಿ!\nವೋಚರ್ ಕೋಡ್: <code>{code}</code>\n(ಡೆಮೊ ವೋಚರ್)",
    },
    "hi": {
        "dist": "📍 आपसे लगभग {km} किमी दूर",
        "camp_rsvp": "✅ <b>{title}</b> के लिए आपका रजिस्ट्रेशन हो गया!\n📍 {venue}\n🗓 {when}\nहम पहले याद दिला देंगे।",
        "camp_thanks": "🎉 <b>{title}</b> में रक्तदान के लिए धन्यवाद! +{points} BLP। अगली रक्तदान तारीख आपकी प्रोफ़ाइल पर है।",
        "rem_camp3": "📅 <b>{title}</b> 3 दिन बाद ({when}), {venue} में है। आ रहे हैं न? अच्छा खाएँ और अच्छी नींद लें।",
        "rem_camp1": "🚨 कल: <b>{title}</b>, {venue}, {when}। ठीक से खाना खाएँ और खूब पानी पिएँ।",
        "rem_camp0": "🩸 आज है! <b>{title}</b>, {venue}, {when}। फ़ोटो पहचान पत्र साथ लाएँ। धन्यवाद, हीरो!",
        "rem_soon": "🩸 {days} दिन बाद आप फिर रक्तदान कर सकते हैं। तैयार रहें: अच्छा खाएँ और खूब पानी पिएँ!",
        "rem_where": " <b>{hospital}</b> में आपके पिछले रक्तदान ने एक जान बचाने में मदद की।",
        "rem_eligible": "🎉 <b>आप फिर से रक्तदान कर सकते हैं!</b>{where}\n\nआज किसी के हीरो बनने के लिए तैयार हैं?",
        "rem_nudge": "💭 अभी सोच रहे हैं? आपके पास के मरीज़ इंतज़ार कर रहे हैं। जब तैयार हों, अलर्ट चालू करें।",
        "rem_available_btn": "✅ मैं उपलब्ध हूँ",
        "rem_later_btn": "⏰ बाद में",
        "achievements": "🎉 <b>उपलब्धि अनलॉक!</b>\n\n{lines}\n\n💰 +{points} BLP मिले\n🏆 अपना संग्रह देखें: /achievements",
        "sos_alert": "🚨 <b>आपातकाल: {group} खून चाहिए</b>\n\n🏥 {hospital}, {city}\n🩸 ज़रूरी यूनिट: {units}\n"
                     "{uicon} तात्कालिकता: {urgency}\n👤 अनुरोधकर्ता: {name}\n\n"
                     "आप मेल खाते डोनर हैं। अस्पताल द्वारा रक्तदान की पुष्टि के बाद जल्दी जवाब देने वालों को +20 BLP बोनस।",
        "donate_btn": "🩸 मैं रक्तदान करूँगा/करूँगी",
        "urg_Critical": "बहुत ज़रूरी", "urg_High": "आज ही", "urg_Normal": "तय ऑपरेशन",
        "donor_coming": "✅ <b>{name}</b> ({group}) {hospital} में आपके अनुरोध के लिए रक्तदान करने आ रहे हैं।{contact}\n"
                        "यूनिट: {done}/{units} — स्थिति: {status}",
        "contact": "\n📞 डोनर का संपर्क: {phone}",
        "st_Active": "सक्रिय", "st_Fulfilled": "पूरा हुआ ✅",
        "ref_joined": "🎉 {name} आपके लिंक से BloodLink से जुड़े! +{points} BLP",
        "staff_pledge": "🩸 अनुरोध #{id} के लिए <b>दाता आ रहे हैं</b>\n👤 {name} ({group}){phone}\n🏥 {hospital}, {city}\n\n"
                        "रक्तदान हो जाने पर <b>दान किया</b> दबाएँ, या <b>नहीं आए</b>। बिना पुष्टि के वादे {hours} घंटे में समाप्त हो जाते हैं।",
        "staff_done_btn": "✅ दान किया",
        "staff_noshow_btn": "❌ नहीं आए",
        "pledge_confirmed": "✅ {hospital} में आपके <b>रक्तदान की पुष्टि हो गई</b>। धन्यवाद!\n+{points} BLP · बैलेंस {balance} BLP\n"
                            "आपकी अगली रक्तदान तिथि: <b>{next}</b>",
        "pledge_missed": "{hospital} में आपके रक्तदान की पुष्टि नहीं हो सकी, इसलिए कोई अंक नहीं जोड़े गए। अगर आपने दान किया है, "
                         "तो कृपया अस्पताल से पुष्टि करने को कहें।{blocked}",
        "pledge_blocked": "\n{n} बिना पुष्टि वाले वादों के बाद, नए वादे {until} तक रोक दिए गए हैं।",
        "staff_lowhb_btn": "🩸 कम Hb",
        "hb_after": "🩸 आपका हीमोग्लोबिन: <b>{hb} g/dL</b> {mark}\nआज: खूब पानी पिएँ और भारी व्यायाम न करें। इस हफ़्ते: आयरन वाला भोजन खाएँ (हरी सब्ज़ियाँ, दाल, गुड़, अंडे या मांस)।",
        "hb_low": "💙 <b>आज आप रक्तदान नहीं कर सके: आपका हीमोग्लोबिन कम था।</b>\n{reading}\n\nयह आम है और आमतौर पर भोजन से सुधर जाता है। आज़माएँ:\n• हरी पत्तेदार सब्ज़ियाँ, दाल और अन्य दलहन\n• गुड़, खजूर, किशमिश और अनार\n• अगर आप खाते हैं तो अंडे, मछली या मांस\n• भोजन के साथ विटामिन सी (नींबू, आँवला, संतरा), और भोजन के आसपास कम चाय या कॉफ़ी\n\nअगर ऐसा फिर हो, तो कृपया डॉक्टर से मिलें। आप <b>{until}</b> से फिर रक्तदान की कोशिश कर सकते हैं।",
        "hb_low_value": "आपका माप {hb} g/dL था; रक्तदान के लिए कम से कम 12.5 g/dL चाहिए।",
        "hb_low_novalue": "यह रक्तदान के लिए ज़रूरी 12.5 g/dL से कम था।",
        "rem_iron": "\n🍽️ सुझाव: इस हफ़्ते आयरन वाला भोजन खाएँ (हरी सब्ज़ियाँ, दाल, गुड़, अंडे या मांस) ताकि हीमोग्लोबिन जाँच में पास हो।",
        "rem_iron_borderline": "\n🍽️ आपका पिछला हीमोग्लोबिन {hb} g/dL था, जो 12.5 की न्यूनतम सीमा के करीब है। इस हफ़्ते रोज़ आयरन वाला भोजन खाएँ (हरी सब्ज़ियाँ, दाल, गुड़, खजूर, अंडे या मांस), थोड़े नींबू या आँवले के साथ।",
        "ride_help": "🆘 <b>{name}</b> ({group}) ने {hospital} में अनुरोध #{id} के लिए वादा किया है और <b>वहाँ पहुँचने में मदद चाहिए</b>।\n📍 {area} से{phone}\nकृपया उन्हें कॉल करें और लाने या कैब की व्यवस्था करें।",
        "ref_donated": "🩸 आपके दोस्त {name} ने अभी रक्तदान किया!\n+{points} BLP और वाउचर: <code>{code}</code>",
        "redeemed": "🎁 आपने <b>{reward}</b> लिया!\nवाउचर कोड: <code>{code}</code>\n(डेमो वाउचर)",
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    table = STRINGS.get(lang or "en", STRINGS["en"])
    return table.get(key, STRINGS["en"][key]).format(**kwargs)

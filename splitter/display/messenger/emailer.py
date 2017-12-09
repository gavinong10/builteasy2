import yagmail

def send_email(recipients, subject, html):
    yag = yagmail.SMTP({'builteasyshortlister@gmail.com': 'Built Easy Shortlister'}, 'BuiltEasy123!')

    yag.send(to=recipients, subject=subject, contents=[html.replace('\n', '')])

#send_email(["gavinong10@gmail.com"], "", "")
